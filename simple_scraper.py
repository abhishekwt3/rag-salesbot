import asyncio
import logging
import random
import time
import hashlib
import io
from typing import List, Dict, Optional, Callable, Any, Set, Tuple
from urllib.parse import urlparse, urlunparse, urljoin, parse_qsl, urlencode

import re
from bs4 import BeautifulSoup

# Optional imports (graceful degradation)
try:
    import trafilatura  # for high-quality text/boilerplate removal
except Exception:  # pragma: no cover
    trafilatura = None

try:
    from pdfminer.high_level import extract_text as pdf_extract_text  # for PDFs
except Exception:  # pragma: no cover
    pdf_extract_text = None

try:
    import httpx  # static fallback client
except Exception:  # pragma: no cover
    httpx = None

from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import urllib.robotparser as robotparser

logger = logging.getLogger("enhanced_scraper")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


# ----------------------------- Utilities -----------------------------

def normalize_url(url: str) -> str:
    """Normalize URL (scheme/host lowercase, sorted query, remove fragments)."""
    parsed = urlparse(url)
    scheme = parsed.scheme.lower() or "http"
    netloc = parsed.netloc.lower()
    path = re.sub(r"/{2,}", "/", parsed.path)  # collapse multiple slashes
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))
    return urlunparse((scheme, netloc, path, "", query, ""))


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def is_probably_pdf(url: str, headers: Optional[Dict[str, str]] = None) -> bool:
    if url.lower().endswith(".pdf"):
        return True
    if headers:
        ct = headers.get("content-type", "").lower()
        return "application/pdf" in ct
    return False


def random_user_agent() -> str:
    ua_pool = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    ]
    return random.choice(ua_pool)


# ----------------------- Rate limiting & concurrency -----------------------

class HostLimiter:
    """Per-host concurrency + simple rate limiting."""
    def __init__(self, max_concurrent: int = 3, min_interval_ms: int = 200):
        self.max_concurrent = max_concurrent
        self.min_interval_ms = min_interval_ms
        self.semaphores: Dict[str, asyncio.Semaphore] = {}
        self.last_hit_ms: Dict[str, float] = {}

    async def throttle(self, host: str):
        sem = self.semaphores.setdefault(host, asyncio.Semaphore(self.max_concurrent))
        async with sem:
            now = time.time() * 1000
            last = self.last_hit_ms.get(host, 0)
            delta = now - last
            if delta < self.min_interval_ms:
                await asyncio.sleep((self.min_interval_ms - delta) / 1000.0)
            self.last_hit_ms[host] = time.time() * 1000


# ----------------------------- Robots manager -----------------------------

class RobotsManager:
    def __init__(self, user_agent: str = "Mozilla/5.0 (compatible; SimpleScraper/1.0)"):
        self.user_agent = user_agent
        self.cache: Dict[str, robotparser.RobotFileParser] = {}

    async def allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"
        rp = self.cache.get(base)
        if not rp:
            rp = robotparser.RobotFileParser()
            robots_url = urljoin(base, "/robots.txt")
            # Fetch robots.txt using httpx if available; otherwise allow by default
            try:
                if httpx:
                    async with httpx.AsyncClient(timeout=10) as client:
                        r = await client.get(robots_url, headers={"User-Agent": self.user_agent})
                        if r.status_code == 200:
                            rp.parse(r.text.splitlines())
                        else:
                            # If no robots or error, default allow (conservative dev choice: allow)
                            rp.parse(["User-agent: *", "Allow: /"])
                else:
                    rp.parse(["User-agent: *", "Allow: /"])
            except Exception:
                rp.parse(["User-agent: *", "Allow: /"])
            self.cache[base] = rp
        return rp.can_fetch(self.user_agent, url)


# ----------------------------- Framework Detection -----------------------------

class FrameworkDetector:
    """Detect website framework and return appropriate scraping strategy"""
    
    @staticmethod
    async def detect_framework(page: Page, url: str) -> str:
        """Detect if the website is a SPA, React, Next.js, or static site"""
        try:
            # Check for framework indicators
            framework_check = await page.evaluate("""
                () => {
                    const indicators = {
                        nextjs: !!(window.__NEXT_DATA__ || document.querySelector('#__next') || 
                                  document.querySelector('[data-nextjs-page]')),
                        react: !!(window.React || document.querySelector('[data-reactroot]') || 
                                 document.querySelector('#root')),
                        spa: !!(document.querySelector('[data-reactroot]') || 
                               document.querySelector('#__next') || 
                               document.querySelector('#root') ||
                               document.querySelector('[ng-app]') ||
                               document.querySelector('[data-ng-app]'))
                    };
                    
                    if (indicators.nextjs) return 'nextjs';
                    if (indicators.react) return 'react';
                    if (indicators.spa) return 'spa';
                    return 'static';
                }
            """)
            
            logger.info(f"🔍 Detected framework: {framework_check} for {url}")
            return framework_check
            
        except Exception as e:
            logger.debug(f"Framework detection failed: {e}")
            return 'static'


# ----------------------------- Enhanced Scraper core -----------------------------

class ScrapedPage:
    def __init__(self, url: str, final_url: str, status: int, html: str, text: str,
                 title: Optional[str], meta_desc: Optional[str], meta: Dict[str, str],
                 framework: str = 'static'):
        self.url = url
        self.final_url = final_url
        self.status = status
        self.html = html
        self.text = text
        self.title = title
        self.meta_desc = meta_desc
        self.meta = meta  # og:title, og:description, canonical, etc.
        self.framework = framework
        self.hash = content_hash(text or html or "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "final_url": self.final_url,
            "status": self.status,
            "hash": self.hash,
            "title": self.title,
            "meta_desc": self.meta_desc,
            "meta": self.meta,
            "text": self.text,
            "html": self.html,
            "framework": self.framework,
            "word_count": len(self.text.split()) if self.text else 0
        }


class EnhancedSimpleScraper:
    def __init__(self,
                 max_retries: int = 3,
                 wait_selector: Optional[str] = "body",
                 host_max_concurrent: int = 3,
                 host_min_interval_ms: int = 200,
                 respect_robots: bool = True,
                 enable_resource_blocking: bool = True,
                 on_result: Optional[Callable[[str, ScrapedPage], Any]] = None):
        self.max_retries = max_retries
        self.wait_selector = wait_selector
        self.enable_resource_blocking = enable_resource_blocking
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.host_limiter = HostLimiter(host_max_concurrent, host_min_interval_ms)
        self.robots = RobotsManager() if respect_robots else None
        self.on_result = on_result  # callback (tenant_id, page)

        # Dedup across a run
        self.seen_urls: Set[str] = set()

    # -------- Playwright lifecycle --------
    async def _ensure_browser(self):
        if self.playwright and self.browser:
            return
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
                "--disable-default-apps",
                "--no-first-run",
            ],
        )
        logger.info("🚀 Enhanced Playwright browser started.")

    async def _close_browser(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        logger.info("🛑 Enhanced Playwright browser closed.")

    async def _new_context(self) -> BrowserContext:
        assert self.browser is not None
        context = await self.browser.new_context(
            user_agent=random_user_agent(),
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            ignore_https_errors=True,
        )
        
        # Set up resource blocking for performance
        if self.enable_resource_blocking:
            await context.route("**/*", self._handle_route)
            logger.info("🚫 Resource blocking enabled for performance")
            
        return context

    async def _handle_route(self, route):
        """Handle route interception to block unnecessary resources for 3-5x performance boost"""
        request = route.request
        resource_type = request.resource_type
        
        # Block unnecessary resources to speed up loading
        if resource_type in ['image', 'media', 'font', 'stylesheet']:
            await route.abort()
        else:
            await route.continue_()

    # -------- Public API --------
    async def scrape_multi_tenant(self, jobs: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        jobs: [{ "tenant_id": str, "urls": [..] }]
        returns { tenant_id: [ScrapedPage.dict(), ...] }
        """
        await self._ensure_browser()
        try:
            tasks = [self._scrape_job(job) for job in jobs]
            results = await asyncio.gather(*tasks)
            return {job["tenant_id"]: pages for job, pages in zip(jobs, results)}
        finally:
            await self._close_browser()

    # -------- Single tenant --------
    async def _scrape_job(self, job: Dict[str, Any]) -> List[Dict[str, Any]]:
        tenant_id = job["tenant_id"]
        urls: List[str] = [normalize_url(u) for u in job.get("urls", [])]
        # Deduplicate input URLs
        unique_urls = []
        seen = set()
        for u in urls:
            if u not in seen:
                unique_urls.append(u)
                seen.add(u)

        ctx = await self._new_context()
        page = await ctx.new_page()

        results: List[Dict[str, Any]] = []
        try:
            for i, url in enumerate(unique_urls):
                if url in self.seen_urls:
                    continue
                self.seen_urls.add(url)

                # robots.txt
                if self.robots:
                    allowed = await self.robots.allowed(url)
                    if not allowed:
                        logger.info(f"🤖 Blocked by robots.txt: {url}")
                        continue

                logger.info(f"📄 Scraping page {i+1}/{len(unique_urls)} for {tenant_id}: {url}")
                sp = await self._fetch_with_retries(page, url)
                if sp:
                    results.append(sp.to_dict())
                    # callback for pipeline (e.g., push to Qdrant)
                    if self.on_result:
                        try:
                            self.on_result(tenant_id, sp)
                        except Exception as cb_err:
                            logger.warning(f"⚠️ on_result callback error for {url}: {cb_err}")
        finally:
            await ctx.close()

        return results

    # -------- Enhanced Fetch logic with progressive fallback --------
    async def _fetch_with_retries(self, page: Page, url: str) -> Optional[ScrapedPage]:
        parsed = urlparse(url)
        host = parsed.netloc

        # Progressive timeout and strategy degradation
        attempt_configs = [
            {"timeout": 60000, "wait_time": 3, "full_framework": True},   # Full attempt
            {"timeout": 30000, "wait_time": 2, "full_framework": False},  # Reduced attempt  
            {"timeout": 15000, "wait_time": 1, "full_framework": False},  # Minimal attempt
        ]

        for attempt in range(1, self.max_retries + 1):
            await self.host_limiter.throttle(host)
            config = attempt_configs[attempt - 1]
            
            try:
                logger.info(f"🌐 [{host}] Attempt {attempt}: Enhanced Playwright GET {url} (timeout={config['timeout']}ms)")
                resp = await page.goto(url, wait_until="networkidle", timeout=config["timeout"])
                status = resp.status if resp else 0

                # Detect framework type (only on first attempt)
                framework = 'static'
                if attempt == 1:
                    framework = await FrameworkDetector.detect_framework(page, url)
                
                # Framework-specific waiting with progressive reduction
                await self._wait_for_framework_content(page, framework, config)

                # Try to click common consent banners (best-effort, no fail)
                await self._dismiss_consent(page)

                html = await page.content()
                final_url = page.url

                # Framework-aware content extraction
                text, title, meta_desc, meta = await self._extract_content_enhanced(page, html, final_url, framework)

                # Heuristic: if text is too small, fallback to static client (attempt 2+)
                if (not text or len(text) < 200) and httpx is not None and attempt >= 2:
                    logger.info(f"📉 [{host}] Dynamic content thin on attempt {attempt}; trying static fallback for {url}")
                    static_page = await self._fetch_static(url)
                    if static_page:
                        return static_page

                return ScrapedPage(url=url, final_url=final_url, status=status, html=html,
                                   text=text, title=title, meta_desc=meta_desc, meta=meta, framework=framework)

            except Exception as e:
                logger.warning(f"⚠️ [{host}] Attempt {attempt} failed for {url}: {e}")
                await asyncio.sleep(self._backoff(attempt))

        # Final fallback to static client
        if httpx is not None:
            logger.info(f"🔄 [{host}] Final fallback: static fetch for {url}")
            return await self._fetch_static(url)

        return None

    async def _wait_for_framework_content(self, page: Page, framework: str, config: Dict):
        """Wait for framework-specific content with progressive timeouts"""
        full_framework = config.get("full_framework", True)
        wait_time = config.get("wait_time", 3)
        base_timeout = min(config.get("timeout", 60000) // 4, 15000)  # 1/4 of page timeout, max 15s
        
        try:
            if framework == 'nextjs' and full_framework:
                logger.info("⚛️ Waiting for Next.js content...")
                await page.wait_for_function(
                    "() => window.__NEXT_DATA__ || document.querySelector('#__next')",
                    timeout=base_timeout
                )
                await page.wait_for_selector("#__next", timeout=base_timeout)
                
            elif framework == 'react' and full_framework:
                logger.info("⚛️ Waiting for React content...")
                await page.wait_for_function(
                    "() => document.querySelector('#root') || document.querySelector('[data-reactroot]')",
                    timeout=base_timeout
                )
                await page.wait_for_selector("#root, [data-reactroot]", timeout=base_timeout)
                
            elif framework == 'spa' and full_framework:
                logger.info("🔄 Waiting for SPA content...")
                await page.wait_for_function(
                    "() => document.querySelector('#root') || document.querySelector('#__next') || document.querySelector('[data-reactroot]')",
                    timeout=base_timeout
                )
                
            # Wait for loading indicators to disappear (reduced timeout on later attempts)
            if full_framework:
                try:
                    await page.wait_for_function(
                        """() => {
                            const loadingElements = document.querySelectorAll(
                                '[class*="loading"], [class*="spinner"], [class*="loader"], [aria-label*="loading"], [aria-label*="Loading"]'
                            );
                            const visibleLoaders = Array.from(loadingElements).filter(el => 
                                el.offsetWidth > 0 && el.offsetHeight > 0
                            );
                            return visibleLoaders.length === 0;
                        }""",
                        timeout=base_timeout
                    )
                    logger.info("✅ Loading indicators cleared")
                except Exception:
                    logger.debug("⚠️ Loading indicator check timed out (proceeding anyway)")
                
            # Basic content wait
            if self.wait_selector:
                try:
                    await page.wait_for_selector(self.wait_selector, timeout=base_timeout)
                except Exception:
                    pass

            # Progressive wait time reduction
            await asyncio.sleep(wait_time)
            
        except Exception as e:
            logger.debug(f"⚠️ Framework-specific waiting failed: {e}")

    async def _extract_content_enhanced(self, page: Page, html: str, url: str, framework: str) -> Tuple[str, Optional[str], Optional[str], Dict[str, str]]:
        """Enhanced content extraction with framework-specific strategies"""
        
        # Try framework-specific extraction first
        if framework in ['nextjs', 'react', 'spa']:
            text = await self._extract_spa_content(page)
            if text and len(text) > 200:
                # Use the SPA-extracted text
                pass
            else:
                # Fallback to trafilatura if SPA extraction failed
                text = self._extract_with_trafilatura(html, url)
        else:
            # Static site - use trafilatura
            text = self._extract_with_trafilatura(html, url)

        # Extract metadata from HTML
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else None
        
        meta_desc = None
        og_title = og_desc = canonical = None
        for m in soup.find_all("meta"):
            if m.get("name", "").lower() == "description" and m.get("content"):
                meta_desc = m["content"].strip()
            if m.get("property") == "og:title" and m.get("content"):
                og_title = m["content"].strip()
            if m.get("property") == "og:description" and m.get("content"):
                og_desc = m["content"].strip()
                
        link_canon = soup.find("link", rel=lambda v: v and "canonical" in v.lower())
        if link_canon and link_canon.get("href"):
            canonical = urljoin(url, link_canon["href"].strip())

        meta = {
            "og:title": og_title or "",
            "og:description": og_desc or "",
            "canonical": canonical or "",
        }
        
        # Enhanced content cleaning
        text = self._clean_content_enhanced(text)
        
        return text, title, meta_desc, meta

    async def _extract_spa_content(self, page: Page) -> str:
        """Extract content from React/Next.js/SPA applications"""
        try:
            content = await page.evaluate("""
                () => {
                    // Strategy 1: Try React/Next.js containers first
                    const containers = [
                        document.getElementById('__next'),
                        document.getElementById('root'),
                        document.querySelector('[data-reactroot]'),
                        document.querySelector('main'),
                        document.querySelector('[role="main"]')
                    ].filter(Boolean);

                    for (const container of containers) {
                        if (container) {
                            const clone = container.cloneNode(true);
                            
                            // Remove scripts, styles, nav elements, and common UI elements
                            const unwanted = clone.querySelectorAll(
                                'script, style, noscript, nav, header, footer, aside, ' +
                                '[class*="nav"], [class*="menu"], [class*="sidebar"], ' +
                                '[class*="header"], [class*="footer"], [role="navigation"], ' +
                                '[class*="cookie"], [class*="banner"]'
                            );
                            unwanted.forEach(el => el.remove());

                            const text = clone.innerText || clone.textContent || '';
                            if (text.length > 200) {
                                return text;
                            }
                        }
                    }

                    // Strategy 2: Try main content areas
                    const selectors = [
                        'main', 'article', '.content', '.main-content', 
                        '.page-content', '[role="main"]', '.container'
                    ];
                    
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const element of elements) {
                            const text = element.innerText || element.textContent || '';
                            if (text.length > 200) {
                                return text;
                            }
                        }
                    }

                    // Strategy 3: Last resort - body text with cleanup
                    const bodyClone = document.body.cloneNode(true);
                    const unwanted = bodyClone.querySelectorAll(
                        'script, style, noscript, nav, header, footer, aside, ' +
                        '[class*="nav"], [class*="menu"], [class*="sidebar"]'
                    );
                    unwanted.forEach(el => el.remove());
                    
                    return bodyClone.innerText || bodyClone.textContent || '';
                }
            """)
            
            return content or ""
            
        except Exception as e:
            logger.error(f"❌ SPA content extraction error: {e}")
            return ""

    def _extract_with_trafilatura(self, html: str, url: str) -> str:
        """Extract content using trafilatura"""
        if trafilatura:
            try:
                extracted = trafilatura.extract(html, include_comments=False, url=url)
                if extracted:
                    return extracted
            except Exception as e:
                logger.debug(f"Trafilatura extraction failed: {e}")
        
        # Fallback to BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def _clean_content_enhanced(self, content: str) -> str:
        """Enhanced content cleaning for modern web frameworks"""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove common boilerplate text patterns
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and very short lines
            if len(line) < 5:
                continue
                
            # Skip common UI/navigation text (enhanced patterns)
            skip_patterns = [
                'home', 'about', 'contact', 'privacy', 'terms', 'policy',
                'cookie', 'subscribe', 'newsletter', 'follow us', 'social',
                'copyright', '©', 'all rights reserved', 'skip to',
                'menu', 'search', 'login', 'sign up', 'cart', 'checkout',
                'loading', 'please wait', 'javascript', 'enable', 'browser',
                'back to top', 'scroll', 'click here', 'read more',
                'share', 'tweet', 'facebook', 'instagram', 'linkedin'
            ]
            
            if len(line) < 50 and any(pattern in line.lower() for pattern in skip_patterns):
                continue
            
            # Skip lines that are mostly symbols, numbers, or very repetitive
            alpha_ratio = len(re.sub(r'[^a-zA-Z]', '', line)) / len(line)
            if alpha_ratio < 0.5 and len(line) < 100:
                continue
            
            # Skip very repetitive lines (like navigation items)
            words = line.lower().split()
            if len(words) > 1:
                unique_words = set(words)
                if len(unique_words) / len(words) < 0.5 and len(line) < 100:
                    continue
            
            cleaned_lines.append(line)
        
        # Join and final cleanup
        content = '\n'.join(cleaned_lines)
        content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 consecutive newlines
        
        # Limit content length to prevent huge pages
        if len(content) > 20000:
            content = content[:20000] + "..."
            
        return content.strip()

    async def _fetch_static(self, url: str) -> Optional[ScrapedPage]:
        if httpx is None:
            return None
        headers = {"User-Agent": random_user_agent(), "Accept": "*/*"}
        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            r = await client.get(url, headers=headers)
            status = r.status_code
            final_url = str(r.url)
            # PDF handling
            if is_probably_pdf(final_url, r.headers):
                text = ""
                if pdf_extract_text:
                    try:
                        text = pdf_extract_text(io.BytesIO(r.content))  # type: ignore
                    except Exception:
                        text = ""
                html = ""
                return ScrapedPage(url=url, final_url=final_url, status=status, html=html,
                                   text=text, title="PDF Document", meta_desc=None, 
                                   meta={}, framework="pdf")
            else:
                html = r.text
                text = self._extract_with_trafilatura(html, final_url)
                soup = BeautifulSoup(html, "html.parser")
                title = soup.title.string.strip() if soup.title and soup.title.string else None
                return ScrapedPage(url=url, final_url=final_url, status=status, html=html,
                                   text=text, title=title, meta_desc=None, 
                                   meta={}, framework="static")
        return None

    # -------- Helpers --------
    def _backoff(self, attempt: int) -> float:
        # Exponential backoff with jitter
        base = 0.5 * (2 ** (attempt - 1))
        return base + random.uniform(0, 0.5)

    async def _dismiss_consent(self, page: Page):
        # Best-effort: click common consent/accept buttons if present
        selectors = [
            "button:has-text('Accept All')",
            "button:has-text('I Agree')",
            "button:has-text('Accept')",
            "button[aria-label='Accept']",
            "text=Accept all cookies",
            "[id*='cookie'] button",
            "[class*='cookie'] button",
            "[id*='consent'] button",
            "[class*='consent'] button",
        ]
        for sel in selectors:
            try:
                el = await page.query_selector(sel)
                if el:
                    await el.click(timeout=2000)
                    await asyncio.sleep(0.5)
                    logger.debug(f"✅ Dismissed consent banner with selector: {sel}")
                    break
            except Exception:
                continue


# Maintain backward compatibility
class SimpleScraper(EnhancedSimpleScraper):
    """Backward compatible alias for EnhancedSimpleScraper"""
    pass


# ----------------------------- Example run -----------------------------

async def main():
    scraper = EnhancedSimpleScraper(
        max_retries=3,
        wait_selector="body",
        host_max_concurrent=3,
        host_min_interval_ms=200,
        respect_robots=True,
        enable_resource_blocking=True,  # 3-5x performance boost
        on_result=lambda tenant, page: logger.info(f"🔗 [PIPELINE] {tenant} <- {page.final_url} ({page.framework}, {page.to_dict()['word_count']} words)"),
    )

    jobs = [
        {
            "tenant_id": "tenant_a",
            "urls": [
                "https://atomberg.com/atomberg-renesa-prime-bldc-motor-3-blade-ceiling-fan",
                "https://www.wikipedia.org/",
                "https://nextjs.org/",  # Next.js site
                "https://react.dev/",   # React site
            ],
        },
        {
            "tenant_id": "tenant_b",
            "urls": [
                "https://example.com/",
            ],
        },
    ]

    results = await scraper.scrape_multi_tenant(jobs)
    for tenant, pages in results.items():
        logger.info(f"🎯 Tenant {tenant} scraped {len(pages)} pages")
        for p in pages:
            logger.info(f"   📄 {p['final_url']} | status={p['status']} | framework={p['framework']} | title={p.get('title')} | words={p['word_count']}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Interrupted by user.")
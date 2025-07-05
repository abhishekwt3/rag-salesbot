# advanced_scraper.py - Playwright scraper that handles JavaScript websites
import asyncio
import logging
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re
from pydantic import BaseModel
from typing import List

# Proper Playwright imports
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from bs4 import BeautifulSoup
import httpx

logger = logging.getLogger(__name__)

class AdvancedPlaywrightScraper:
    """Advanced Playwright scraper that handles JavaScript-heavy websites"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None   
        
    async def scrape_website(self, base_url: str, max_pages: int = 10, 
                           include_patterns: List[str] = None, 
                           exclude_patterns: List[str] = None) -> List[Dict]:
        """Advanced scraping with JavaScript support"""
        
        if include_patterns is None:
            include_patterns = []
        if exclude_patterns is None:
            exclude_patterns = []
            
        logger.info(f"🎭 Starting advanced Playwright scraping for: {base_url}")
        logger.info(f"⚡ JavaScript rendering enabled")
        
        pages_data = []
        urls_to_visit = [base_url]
        visited_urls = set()
        
        try:
            # Initialize advanced browser setup
            await self._init_advanced_browser()
            
            for i, url in enumerate(urls_to_visit[:max_pages]):
                if url in visited_urls:
                    continue
                    
                visited_urls.add(url)
                logger.info(f"🔄 Scraping ({i+1}/{min(max_pages, len(urls_to_visit))}): {url}")
                
                try:
                    # Advanced page scraping with JavaScript handling
                    page_data = await self._scrape_page_with_js(url)
                    
                    if page_data and page_data.get('content'):
                        pages_data.append(page_data)
                        logger.info(f"✅ Success: {len(page_data['content'])} chars - '{page_data['title'][:50]}'")
                        
                        # Extract URLs from JavaScript-rendered content
                        new_urls = self._extract_urls_enhanced(
                            page_data.get('links', []), base_url, include_patterns, exclude_patterns
                        )
                        
                        for new_url in new_urls:
                            if new_url not in visited_urls and new_url not in urls_to_visit:
                                urls_to_visit.append(new_url)
                                
                        logger.info(f"   🔗 Found {len(new_urls)} new URLs")
                    else:
                        logger.warning(f"⚠️  No content extracted from {url}")
                    
                    # Human-like delay
                    delay = random.uniform(3, 7)
                    logger.info(f"   ⏳ Waiting {delay:.1f}s (human-like behavior)...")
                    await asyncio.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"❌ Error scraping {url}: {e}")
                    # Try to recover browser
                    try:
                        await self._recover_browser()
                    except Exception as recover_error:
                        logger.error(f"Browser recovery failed: {recover_error}")
                        break  # Exit if browser can't be recovered
                    continue
                    
        except Exception as e:
            logger.error(f"💥 Fatal scraping error: {e}")
        finally:
            await self._cleanup()
            
        logger.info(f"🎯 Advanced scraping completed: {len(pages_data)} pages scraped")
        return pages_data
    
    async def _init_advanced_browser(self):
        """Initialize browser with advanced anti-detection and JavaScript support"""
        try:
            # Start Playwright
            self.playwright = await async_playwright().start()
            
            # Launch browser with comprehensive settings
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # Set to False for debugging
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-web-security',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--window-size=1920,1080'
                ]
            )
            
            # Create context with realistic browser fingerprint
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                permissions=['geolocation'],
                geolocation={'longitude': -74.006, 'latitude': 40.7128},  # New York
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            # Advanced anti-detection script
            await self.context.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                
                // Mock chrome runtime
                window.chrome = {
                    runtime: {},
                    loadTimes: function() {},
                    csi: function() {},
                    app: {}
                };
                
                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [
                        {
                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                            description: "Portable Document Format",
                            filename: "internal-pdf-viewer",
                            length: 1,
                            name: "Chrome PDF Plugin"
                        },
                        {
                            0: {type: "application/pdf", suffixes: "pdf", description: ""},
                            description: "",
                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                            length: 1,
                            name: "Chrome PDF Viewer"
                        }
                    ],
                });
                
                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
                );
                
                // Hide automation indicators
                const originalCall = Function.prototype.call;
                function showMethodCall(event) {
                    return originalCall;
                }
                Function.prototype.call = showMethodCall;
                
                const originalApply = Function.prototype.apply;
                function showMethodApply(event) {
                    return originalApply;
                }
                Function.prototype.apply = showMethodApply;
                
                // Mock timezone
                Intl.DateTimeFormat = class extends Intl.DateTimeFormat {
                    constructor() {
                        super();
                        this.resolvedOptions = () => ({ timeZone: 'America/New_York' });
                    }
                };
            """)
            
            logger.info("✅ Advanced browser initialized with anti-detection")
            
        except Exception as e:
            logger.error(f"Failed to initialize advanced browser: {e}")
            raise
    
    async def _scrape_page_with_js(self, url: str) -> Optional[Dict]:
        page = None
        try:
            # Create new page
            page = await self.context.new_page()
            
            # UPDATED: Longer timeouts for SPAs
            page.set_default_timeout(90000)  # 90 seconds for SPAs
            page.set_default_navigation_timeout(60000)
            
            logger.info(f"   🌐 Loading page with JavaScript rendering...")
            
            # Navigate with multiple retry attempts
            for attempt in range(3):
                try:
                    # Navigate to page
                    response = await page.goto(
                        url, 
                        wait_until='networkidle',  # Wait for network to be idle
                        timeout=60000
                    )
                    
                    if response:
                        status = response.status
                        logger.info(f"   📊 Response status: {status}")
                        
                        if status == 403:
                            logger.warning(f"   🚫 Access forbidden: {url}")
                            return None
                        elif status == 429:
                            logger.warning(f"   ⏰ Rate limited, waiting longer...")
                            await asyncio.sleep(random.uniform(15, 30))
                            continue
                        elif status >= 400:
                            logger.warning(f"   ❌ HTTP error {status}: {url}")
                            return None
                    
                    break  # Success
                    
                except Exception as nav_error:
                    logger.warning(f"   ⚠️  Navigation attempt {attempt + 1} failed: {nav_error}")
                    if attempt < 2:
                        await asyncio.sleep(random.uniform(5, 10))
                        continue
                    else:
                        raise nav_error
            
            # UPDATED: Enhanced waiting strategies for React/Next.js
            logger.info("   ⏳ Waiting for JavaScript content to render...")
            
            # Check if it's a SPA
            is_spa = await page.evaluate("""
                () => {
                    const html = document.documentElement.innerHTML;
                    return html.includes('id="__next"') || 
                        html.includes('id="root"') || 
                        html.includes('react') ||
                        html.includes('next.js');
                }
            """)
            
            if is_spa:
                logger.info("   🎭 Detected React/Next.js SPA - using enhanced waiting...")
                
                # Strategy 1: Wait for React to mount
                try:
                    await page.wait_for_function(
                        """
                        () => {
                            const nextDiv = document.getElementById('__next') || document.getElementById('root');
                            return nextDiv && nextDiv.children.length > 0;
                        }
                        """,
                        timeout=30000
                    )
                    logger.info("   ✅ React app mounted successfully")
                except Exception as e:
                    logger.warning(f"   ⚠️  React mount detection failed: {e}")
                
                # Strategy 2: Wait for content to appear
                try:
                    await page.wait_for_function(
                        """
                        () => {
                            const container = document.getElementById('__next') || 
                                            document.getElementById('root') || 
                                            document.body;
                            const textContent = container.innerText || '';
                            return textContent.length > 200;
                        }
                        """,
                        timeout=45000
                    )
                    logger.info("   ✅ Content detected in SPA container")
                except Exception as e:
                    logger.warning(f"   ⚠️  SPA content detection failed: {e}")
                
                # Strategy 3: Wait for loading indicators to disappear
                try:
                    await page.wait_for_function(
                        """
                        () => {
                            const loadingElements = document.querySelectorAll(
                                '[class*="loading"], [class*="spinner"], [aria-label*="loading"], .loader'
                            );
                            const visibleLoaders = Array.from(loadingElements).filter(el => 
                                el.offsetWidth > 0 && el.offsetHeight > 0
                            );
                            return visibleLoaders.length === 0;
                        }
                        """,
                        timeout=30000
                    )
                    logger.info("   ✅ Loading indicators cleared")
                except Exception as e:
                    logger.warning(f"   ⚠️  Loading indicator check failed: {e}")
                
                # Additional wait for SPA
                await asyncio.sleep(5)
                
            else:
                # Regular JavaScript site handling
                logger.info("   ⚡ Regular JavaScript site - using standard waiting...")
                
                # Your existing wait strategies
                try:
                    await page.wait_for_function(
                        "document.readyState === 'complete'",
                        timeout=20000
                    )
                    logger.info("   ✅ Document ready state complete")
                    
                    await page.wait_for_function(
                        "document.body && document.body.innerText.length > 100",
                        timeout=30000
                    )
                    logger.info("   ✅ Body content detected")
                    
                except Exception as wait_error:
                    logger.warning(f"   ⚠️  Wait strategy failed: {wait_error}")
                
                # Your existing additional wait
                await asyncio.sleep(5)
            
            # Try to trigger any lazy loading by scrolling (your existing code)
            try:
                await page.evaluate("""
                    window.scrollTo(0, document.body.scrollHeight / 4);
                """)
                await asyncio.sleep(2)
                await page.evaluate("""
                    window.scrollTo(0, 0);
                """)
                await asyncio.sleep(2)
            except Exception as scroll_error:
                logger.debug(f"   Scrolling failed: {scroll_error}")
            
            # UPDATED: Enhanced content extraction
            logger.info("   📄 Extracting JavaScript-rendered content...")
            
            # Get page title
            title = await page.title()
            logger.info(f"   📄 Page title: '{title}'")
            
            # UPDATED: Use enhanced extraction method
            if is_spa:
                content = await self._extract_spa_content(page)
                links = await self._extract_spa_links(page)
            else:
                # Your existing content extraction
                content = await self._extract_regular_content(page)
                links = await self._extract_regular_links(page)
            
            # Clean and validate content (your existing code)
            if content:
                content = self._clean_content(content)
            
            # Debug output
            logger.info(f"   📊 Final content length: {len(content)} chars")
            if content:
                logger.info(f"   📊 Content preview: '{content[:200]}...'")
            
            # Validate content quality
            if not content or len(content) < 50:
                logger.warning(f"   ⚠️  Insufficient content after JavaScript rendering: {len(content)} chars")
                
                # Enhanced debugging for SPAs
                if is_spa:
                    spa_debug = await page.evaluate("""
                        () => {
                            const container = document.getElementById('__next') || 
                                            document.getElementById('root');
                            return {
                                containerExists: !!container,
                                containerChildren: container ? container.children.length : 0,
                                containerText: container ? container.innerText.substring(0, 300) : '',
                                bodyText: document.body.innerText.substring(0, 300),
                                hasNextData: !!window.__NEXT_DATA__
                            };
                        }
                    """)
                    logger.info(f"   🔍 SPA Debug: {spa_debug}")
                
                if len(content) < 50:
                    return None
            
            # Success!
            return {
                'url': url,
                'title': title,
                'content': content,
                'links': links,
                'scraped_at': time.time(),
                'method': 'playwright_enhanced_spa' if is_spa else 'playwright_javascript',
                'word_count': len(content.split()) if content else 0,
                'is_spa': is_spa
            }
            
        except Exception as e:
            logger.error(f"   ❌ JavaScript scraping error for {url}: {e}")
            return None
        finally:
            if page:
                try:
                    await page.close()
                except Exception as close_error:
                    logger.debug(f"   Page close error: {close_error}")
    
    async def _recover_browser(self):
        """Recover browser after crash"""
        logger.info("🔄 Recovering browser...")
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.debug(f"Cleanup during recovery failed: {e}")
        
        # Re-initialize
        await self._init_advanced_browser()
        logger.info("✅ Browser recovered successfully")
    
    def _clean_content(self, content: str) -> str:
        """Enhanced content cleaning for JavaScript-rendered content"""
        if not content:
            return ""
        
        # Split into lines and clean
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip very short lines and common UI text
            if len(line) > 5 and not any(skip in line.lower() for skip in [
                'loading', 'please wait', 'skip to', 'menu', 'search',
                'cookie', 'privacy policy', 'terms of service',
                'subscribe', 'sign up', 'login', 'log in',
                'javascript', 'enable cookies', 'browser support'
            ]):
                cleaned_lines.append(line)
        
        # Join and clean
        content = ' '.join(cleaned_lines)
        content = ' '.join(content.split())  # Remove extra whitespace
        
        # Limit length
        if len(content) > 15000:
            content = content[:15000] + "..."
        
        return content
    
    def _extract_urls_enhanced(self, links: List[Dict], base_url: str, 
                             include_patterns: List[str], exclude_patterns: List[str]) -> List[str]:
        """Extract URLs from JavaScript-rendered links"""
        base_domain = urlparse(base_url).netloc
        valid_urls = []
        
        for link in links:
            try:
                href = link.get('href', '').strip()
                if not href:
                    continue
                
                # Handle different URL formats
                if href.startswith('javascript:') or href.startswith('mailto:') or href.startswith('tel:'):
                    continue
                
                # Convert to absolute URL
                if href.startswith('/'):
                    full_url = f"{urlparse(base_url).scheme}://{base_domain}{href}"
                elif href.startswith('#'):
                    continue  # Skip anchor links
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(base_url, href)
                
                parsed_url = urlparse(full_url)
                
                # Only same domain
                if parsed_url.netloc != base_domain:
                    continue
                
                # Apply filters
                if include_patterns and not any(pattern.lower() in full_url.lower() for pattern in include_patterns):
                    continue
                
                if exclude_patterns and any(pattern.lower() in full_url.lower() for pattern in exclude_patterns):
                    continue
                
                # Clean URL
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                
                if clean_url not in valid_urls and clean_url != base_url:
                    valid_urls.append(clean_url)
                    
            except Exception as e:
                logger.debug(f"URL processing error for {href}: {e}")
                continue
        
        return valid_urls

    async def _extract_spa_content(self, page) -> str:
        """Extract content from React/Next.js SPAs"""
        try:
            content = await page.evaluate("""
                () => {
                    // Try React/Next.js container first
                    const containers = [
                        document.getElementById('__next'),
                        document.getElementById('root'),
                        document.querySelector('[data-reactroot]')
                    ].filter(Boolean);

                    for (const container of containers) {
                        if (container) {
                            const clone = container.cloneNode(true);
                            // Remove scripts, styles, nav elements
                            const unwanted = clone.querySelectorAll(
                                'script, style, noscript, nav, header, footer, [class*="nav"], [class*="menu"]'
                            );
                            unwanted.forEach(el => el.remove());

                            const text = clone.innerText || clone.textContent || '';
                            if (text.length > 200) {
                                return text;
                            }
                        }
                    }

                    // Fallback to main content areas
                    const selectors = ['main', 'article', '.content', '.main-content', 'section'];
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const element of elements) {
                            const text = element.innerText || element.textContent || '';
                            if (text.length > 200) {
                                return text;
                            }
                        }
                    }

                    // Last resort: all body text
                    return document.body.innerText || document.body.textContent || '';
                }
            """)

            return content or ""
        except Exception as e:
            logger.error(f"SPA content extraction error: {e}")
            return ""

    async def _extract_spa_links(self, page) -> list:
        """Extract links from React/Next.js SPAs"""
        try:
            links = await page.evaluate("""
                () => {
                    const linkElements = document.querySelectorAll('a[href], [role="link"]');
                    const links = [];

                    linkElements.forEach(link => {
                        let href = link.href || link.getAttribute('href') || '';
                        const text = (link.innerText || link.textContent || '').trim();

                        // Handle Next.js Link components and relative URLs
                        if (href.startsWith('/')) {
                            href = window.location.origin + href;
                        }

                        if (href && text && !href.includes('javascript:')) {
                            links.push({
                                href: href,
                                text: text
                            });
                        }
                    });

                    return links;
                }
            """)

            return links or []
        except Exception as e:
            logger.warning(f"SPA link extraction error: {e}")
            return []

    async def _extract_regular_content(self, page) -> str:
        """Your existing content extraction for regular sites"""
        content = ""
        content_selectors = [
            'main', 'article', '[role="main"]',
            '.content', '.main-content', '#content', '#main', '.container'
        ]

        for selector in content_selectors:
            try:
                elements = await page.query_selector_all(selector)
                if elements:
                    for element in elements:
                        text = await element.inner_text()
                        if text and len(text) > len(content):
                            content = text
                            logger.info(f"   📄 Content from {selector}: {len(text)} chars")
                    if len(content) > 500:
                        break
            except Exception as e:
                logger.debug(f"   Selector {selector} failed: {e}")

        # Your existing fallback methods...
        if len(content) < 200:
            try:
                content = await page.evaluate("""
                    () => {
                        const body = document.body;
                        if (!body) return '';

                        const scripts = body.querySelectorAll('script, style, noscript');
                        scripts.forEach(el => el.remove());

                        return body.innerText || body.textContent || '';
                    }
                """)
            except Exception as e:
                logger.warning(f"Body text extraction failed: {e}")

        return content

    async def _extract_regular_links(self, page) -> list:
        """Your existing link extraction"""
        try:
            links_data = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    return links.map(link => ({
                        href: link.href,
                        text: link.textContent.trim()
                    }));
                }
            """)
            return links_data or []
        except Exception as e:
            logger.warning(f"Link extraction failed: {e}")
            return []
        
    
# Updated WebScraper class that uses the advanced Playwright scraper
class WebScraper:
    """Enhanced WebScraper with JavaScript support"""
    
    def __init__(self):
        self.playwright_scraper = AdvancedPlaywrightScraper()
        # Fallback HTTP scraper (from previous version)
        self.http_scraper = None
        
    async def scrape_website(self, base_url: str, max_pages: int = 50, 
                           include_patterns: List[str] = None, 
                           exclude_patterns: List[str] = None) -> List[Dict]:
        """Main scraping method with JavaScript support"""
        
        logger.info("🎭 Using advanced Playwright scraper with JavaScript rendering")
        
        try:
            # Try advanced Playwright scraping first
            pages = await self.playwright_scraper.scrape_website(
                base_url, max_pages, include_patterns, exclude_patterns
            )
            
            if pages and len(pages) > 0:
                logger.info(f"✅ Playwright with JavaScript succeeded: {len(pages)} pages")
                return pages
            else:
                logger.warning("⚠️  Playwright got 0 pages")
                
        except Exception as e:
            logger.error(f"❌ Playwright scraping failed: {e}")
            
        # If we get here, Playwright failed - you can add HTTP fallback here if needed
        logger.info("💡 For JavaScript-heavy sites, manual content addition is recommended")
        return []
    

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
import httpxc

logger = logging.getLogger(__name__)

class AdvancedPlaywrightScraper:
    """Advanced Playwright scraper that handles JavaScript-heavy websites"""
    
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        
    async def scrape_website(self, base_url: str, max_pages: int = 50, 
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
        """Scrape page with comprehensive JavaScript handling"""
        page = None
        try:
            # Create new page
            page = await self.context.new_page()
            
            # Set comprehensive timeouts
            page.set_default_timeout(60000)  # 60 seconds
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
            
            # CRITICAL: Wait for JavaScript content to load
            logger.info("   ⏳ Waiting for JavaScript content to render...")
            
            # Multiple wait strategies for JavaScript content
            try:
                # Strategy 1: Wait for common content indicators
                await page.wait_for_function(
                    "document.readyState === 'complete'",
                    timeout=20000
                )
                logger.info("   ✅ Document ready state complete")
                
                # Strategy 2: Wait for body to have content
                await page.wait_for_function(
                    "document.body && document.body.innerText.length > 100",
                    timeout=30000
                )
                logger.info("   ✅ Body content detected")
                
            except Exception as wait_error:
                logger.warning(f"   ⚠️  Wait strategy failed: {wait_error}")
                # Continue anyway - content might still be there
            
            # Additional wait for slow-loading content
            logger.info("   ⏳ Additional wait for dynamic content...")
            await asyncio.sleep(5)
            
            # Try to trigger any lazy loading by scrolling
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
            
            # Extract content using multiple methods
            logger.info("   📄 Extracting JavaScript-rendered content...")
            
            # Get page title
            title = await page.title()
            logger.info(f"   📄 Page title: '{title}'")
            
            # Method 1: Try to get text from main content areas
            content = ""
            content_selectors = [
                'main',
                'article',
                '[role="main"]',
                '.content',
                '.main-content',
                '#content',
                '#main',
                '.container'
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
            
            # Method 2: Fallback to body text
            if len(content) < 200:
                try:
                    logger.info("   📄 Trying body text extraction...")
                    content = await page.evaluate("""
                        () => {
                            const body = document.body;
                            if (!body) return '';
                            
                            // Remove script and style content
                            const scripts = body.querySelectorAll('script, style, noscript');
                            scripts.forEach(el => el.remove());
                            
                            return body.innerText || body.textContent || '';
                        }
                    """)
                    logger.info(f"   📄 Body text: {len(content)} chars")
                except Exception as e:
                    logger.warning(f"   ⚠️  Body text extraction failed: {e}")
            
            # Method 3: Last resort - get all visible text
            if len(content) < 100:
                try:
                    logger.info("   📄 Trying comprehensive text extraction...")
                    content = await page.evaluate("""
                        () => {
                            // Get all text nodes
                            const walker = document.createTreeWalker(
                                document.body,
                                NodeFilter.SHOW_TEXT,
                                {
                                    acceptNode: function(node) {
                                        // Skip hidden elements
                                        const parent = node.parentElement;
                                        if (!parent) return NodeFilter.FILTER_REJECT;
                                        
                                        const style = window.getComputedStyle(parent);
                                        if (style.display === 'none' || 
                                            style.visibility === 'hidden' ||
                                            style.opacity === '0') {
                                            return NodeFilter.FILTER_REJECT;
                                        }
                                        
                                        return NodeFilter.FILTER_ACCEPT;
                                    }
                                }
                            );
                            
                            let text = '';
                            let node;
                            while (node = walker.nextNode()) {
                                const nodeText = node.textContent.trim();
                                if (nodeText.length > 3) {
                                    text += nodeText + ' ';
                                }
                            }
                            
                            return text.trim();
                        }
                    """)
                    logger.info(f"   📄 Comprehensive text: {len(content)} chars")
                except Exception as e:
                    logger.warning(f"   ⚠️  Comprehensive extraction failed: {e}")
            
            # Get all links
            links = []
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
                links = links_data or []
                logger.info(f"   🔗 Extracted {len(links)} links")
            except Exception as e:
                logger.warning(f"   ⚠️  Link extraction failed: {e}")
            
            # Clean and validate content
            if content:
                content = self._clean_content(content)
            
            # Debug output
            logger.info(f"   📊 Final content length: {len(content)} chars")
            if content:
                logger.info(f"   📊 Content preview: '{content[:200]}...'")
            
            # Validate content quality
            if not content or len(content) < 50:
                logger.warning(f"   ⚠️  Insufficient content after JavaScript rendering: {len(content)} chars")
                
                # Debug: Take screenshot for inspection
                try:
                    screenshot_path = f"debug_screenshot_{int(time.time())}.png"
                    await page.screenshot(path=screenshot_path)
                    logger.info(f"   📷 Debug screenshot saved: {screenshot_path}")
                except Exception as screenshot_error:
                    logger.debug(f"   Screenshot failed: {screenshot_error}")
                
                # Show what's actually on the page
                try:
                    page_html = await page.content()
                    logger.info(f"   🔍 Page HTML length: {len(page_html)}")
                    
                    # Check for common JavaScript frameworks
                    html_lower = page_html.lower()
                    frameworks = {
                        'React': 'react' in html_lower,
                        'Vue': 'vue' in html_lower,
                        'Angular': 'angular' in html_lower,
                        'jQuery': 'jquery' in html_lower
                    }
                    
                    detected = [name for name, found in frameworks.items() if found]
                    if detected:
                        logger.info(f"   🔍 Detected frameworks: {', '.join(detected)}")
                    
                except Exception as debug_error:
                    logger.debug(f"   Debug inspection failed: {debug_error}")
                
                if len(content) < 50:
                    return None
            
            # Success!
            return {
                'url': url,
                'title': title,
                'content': content,
                'links': links,
                'scraped_at': time.time(),
                'method': 'playwright_javascript',
                'word_count': len(content.split()) if content else 0
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
    
    async def _cleanup(self):
        """Enhanced cleanup"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception as e:
            logger.warning(f"Cleanup warning: {e}")
        
        logger.info("🧹 Advanced browser cleanup completed")
    


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
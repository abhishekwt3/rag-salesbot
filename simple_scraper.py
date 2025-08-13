# simple_scraper.py - Advanced web scraper for dynamic content (Next.js, React, SPAs)
import asyncio
import logging
import time
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
import re

from playwright.async_api import async_playwright, Page, BrowserContext
from bs4 import BeautifulSoup
import httpx
from posthog import page

logger = logging.getLogger(__name__)

class AdvancedWebScraper:
    """Advanced web scraper that handles dynamic content, SPAs, and JavaScript-heavy sites"""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        
    async def scrape_website(self, base_url: str, config: Dict) -> List[Dict]:
        """
        Scrape website content with advanced JavaScript handling
        
        Args:
            base_url: Starting URL to scrape
            config: Configuration dictionary with scraping parameters
            
        Returns:
            List of page dictionaries with content
        """
        pages = []
        
        try:
            # Initialize Playwright browser
            await self._init_browser()
            
            if config.get('single_page_mode', False):
                # Single page mode - scrape just the given URL
                page_content = await self._scrape_single_page_dynamic(base_url)
                if page_content:
                    pages.append(page_content)
            else:
                # Multi-page mode - discover and scrape multiple pages
                pages = await self._scrape_multiple_pages_dynamic(base_url, config)
                
        except Exception as e:
            logger.error(f"Error scraping website {base_url}: {e}")
            
        finally:
            await self._cleanup()
            
        return pages
    
    async def _init_browser(self):
        """Initialize Playwright browser with optimized settings"""
        playwright = await async_playwright().start()
        
        # Launch browser with optimizations for scraping
        self.browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--disable-extensions',
                '--disable-default-apps'
            ]
        )
        
        # Create context with realistic user agent and settings
        self.context = await self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            ignore_https_errors=True
        )
        
        # Set up request interception to block unnecessary resources
        await self.context.route("**/*", self._handle_route)
        
    async def _handle_route(self, route):
        """Handle route interception to optimize loading"""
        request = route.request
        resource_type = request.resource_type
        
        # Block unnecessary resources to speed up loading
        if resource_type in ['image', 'media', 'font', 'stylesheet']:
            await route.abort()
        else:
            await route.continue_()
    
    async def _scrape_single_page_dynamic(self, url: str) -> Optional[Dict]:
        """Scrape with better timeout handling"""
        try:
            page = await self.context.new_page()
            logger.info(f"📄 Scraping: {url}")        
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            await page.wait_for_timeout(2000)
            page_data = await self._extract_page_content_dynamic(page, url)
            await page.close()
            return page_data
        
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            if page:
                try:
                    await page.close()
                except:
                    pass
            return None
    
    async def _scrape_multiple_pages_dynamic(self, base_url: str, config: Dict) -> List[Dict]:
        """Scrape multiple pages with JavaScript support"""
        pages = []
        visited_urls: Set[str] = set()
        urls_to_visit = [base_url]
        max_pages = config.get('max_pages', 50)
        include_patterns = config.get('include_patterns', [])
        exclude_patterns = config.get('exclude_patterns', ['/blog', '/news'])
        
        domain = urlparse(base_url).netloc
        
        try:
            page = await self.context.new_page()
            
            while urls_to_visit and len(pages) < max_pages:
                current_url = urls_to_visit.pop(0)
                
                if current_url in visited_urls:
                    continue
                    
                visited_urls.add(current_url)
                
                # Check if URL should be excluded
                if self._should_exclude_url(current_url, exclude_patterns):
                    continue
                
                # Check if URL should be included (if patterns specified)
                if include_patterns and not self._should_include_url(current_url, include_patterns):
                    continue
                
                logger.info(f"🔍 Scraping page {len(pages) + 1}/{max_pages}: {current_url}")
                
                try:
                    # Navigate to page
                    await page.goto(current_url, wait_until='domcontentloaded', timeout=15000)
                    await page.wait_for_timeout(2000)
                    
                    # Wait for dynamic content
                    await self._wait_for_dynamic_content(page)
                    
                    # Extract page content
                    page_data = await self._extract_page_content_dynamic(page, current_url)
                    if page_data:
                        pages.append(page_data)
                    
                    # Find more URLs to scrape (handle SPAs and dynamic links)
                    if len(pages) < max_pages:
                        new_urls = await self._extract_links_dynamic(page, current_url, domain)
                        for url in new_urls:
                            if url not in visited_urls and url not in urls_to_visit:
                                urls_to_visit.append(url)
                    
                    # Rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping {current_url}: {e}")
                    continue
            
            await page.close()
                        
        except Exception as e:
            logger.error(f"Error in multi-page dynamic scraping: {e}")
        
        logger.info(f"✅ Scraped {len(pages)} pages from {base_url}")
        return pages
    
    async def _wait_for_dynamic_content(self, page: Page):
        """Wait for dynamic content to load using multiple strategies"""
        try:
            # Strategy 1: Wait for common loading indicators to disappear
            loading_selectors = [
                '[data-testid="loading"]',
                '.loading',
                '.spinner',
                '.loader',
                '[aria-label*="loading" i]',
                '[aria-label*="Loading" i]'
            ]
            
            for selector in loading_selectors:
                try:
                    await page.wait_for_selector(selector, state='detached', timeout=5000)
                except:
                    continue
            
            # Strategy 2: Wait for common content containers
            content_selectors = [
                'main',
                '[role="main"]', 
                '.content',
                '#content',
                '.main-content',
                'article',
                '.post-content',
                '.page-content'
            ]
            
            for selector in content_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=3000)
                    break
                except:
                    continue
            
            # Strategy 3: Wait for React/Next.js specific indicators
            try:
                # Wait for React to be ready
                await page.wait_for_function(
                    "() => window.React || window.__NEXT_DATA__ || document.querySelector('[data-reactroot]')",
                    timeout=5000
                )
            except:
                pass
            
            # Strategy 4: Wait for network to be idle
            try:
                await page.wait_for_load_state('networkidle', timeout=10000)
            except:
                pass
            
            # Strategy 5: Additional wait for lazy-loaded content
            await asyncio.sleep(2)
            
            # Strategy 6: Scroll to trigger lazy loading
            await self._trigger_lazy_loading(page)
            
        except Exception as e:
            logger.debug(f"Dynamic content waiting completed with some timeouts: {e}")
    
    async def _trigger_lazy_loading(self, page: Page):
        """Scroll through page to trigger lazy loading"""
        try:
            # Get page height
            page_height = await page.evaluate("document.body.scrollHeight")
            
            # Scroll in steps to trigger lazy loading
            steps = min(5, max(2, page_height // 1000))
            for i in range(steps):
                scroll_to = (page_height // steps) * (i + 1)
                await page.evaluate(f"window.scrollTo(0, {scroll_to})")
                await asyncio.sleep(1)
            
            # Scroll back to top
            await page.evaluate("window.scrollTo(0, 0)")
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.debug(f"Lazy loading trigger failed: {e}")
    
    async def _extract_page_content_dynamic(self, page: Page, url: str) -> Optional[Dict]:
        """Extract content from a dynamically loaded page"""
        try:
            # Get page title
            title = await page.title()
            if not title:
                title = url
            
            # Get page content using multiple strategies
            content = await self._extract_content_strategies(page)
            
            # Clean up content
            content = self._clean_content(content)
            
            if content and len(content.strip()) > 100:  # Minimum content length
                return {
                    'url': url,
                    'title': title.strip(),
                    'content': content,
                    'scraped_at': time.time()
                }
                
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            
        return None
    
    async def _extract_content_strategies(self, page: Page) -> str:
        """Use multiple strategies to extract content"""
        content_parts = []
        
        try:
            # Strategy 1: Try to get structured data (JSON-LD, etc.)
            structured_content = await self._extract_structured_data(page)
            if structured_content:
                content_parts.append(structured_content)
            
            # Strategy 2: Extract from main content areas
            main_content = await self._extract_main_content(page)
            if main_content:
                content_parts.append(main_content)
            
            # Strategy 3: Extract from Next.js specific patterns
            nextjs_content = await self._extract_nextjs_content(page)
            if nextjs_content:
                content_parts.append(nextjs_content)
            
            # Strategy 4: Extract from React components
            react_content = await self._extract_react_content(page)
            if react_content:
                content_parts.append(react_content)
            
            # Strategy 5: Fallback to body content
            if not content_parts:
                body_content = await page.evaluate("""
                    () => {
                        // Remove script and style elements
                        const scripts = document.querySelectorAll('script, style, nav, header, footer, aside');
                        scripts.forEach(el => el.remove());
                        
                        return document.body ? document.body.innerText : '';
                    }
                """)
                if body_content:
                    content_parts.append(body_content)
            
        except Exception as e:
            logger.error(f"Error in content extraction strategies: {e}")
        
        return '\n\n'.join(content_parts)
    
    async def _extract_structured_data(self, page: Page) -> str:
        """Extract structured data (JSON-LD, microdata)"""
        try:
            structured_data = await page.evaluate("""
                () => {
                    const jsonLdScripts = document.querySelectorAll('script[type="application/ld+json"]');
                    let content = '';
                    
                    jsonLdScripts.forEach(script => {
                        try {
                            const data = JSON.parse(script.textContent);
                            if (data.description) content += data.description + '\\n';
                            if (data.text) content += data.text + '\\n';
                            if (data.articleBody) content += data.articleBody + '\\n';
                        } catch (e) {}
                    });
                    
                    return content;
                }
            """)
            return structured_data
        except:
            return ""
    
    async def _extract_main_content(self, page: Page) -> str:
        """Extract from main content areas"""
        try:
            main_content = await page.evaluate("""
                () => {
                    const selectors = [
                        'main', 
                        '[role="main"]', 
                        '.content', 
                        '#content',
                        '.main-content', 
                        '#main-content', 
                        'article',
                        '.post-content', 
                        '.entry-content',
                        '.page-content'
                    ];
                    
                    for (const selector of selectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            // Remove unwanted elements
                            const unwanted = element.querySelectorAll('script, style, nav, header, footer, aside, .ad, .advertisement');
                            unwanted.forEach(el => el.remove());
                            
                            return element.innerText;
                        }
                    }
                    return '';
                }
            """)
            return main_content
        except:
            return ""
    
    async def _extract_nextjs_content(self, page: Page) -> str:
        """Extract content from Next.js specific patterns"""
        try:
            nextjs_content = await page.evaluate("""
                () => {
                    // Try to get content from Next.js data
                    if (window.__NEXT_DATA__) {
                        try {
                            const data = window.__NEXT_DATA__;
                            let content = '';
                            
                            // Extract from page props
                            if (data.props && data.props.pageProps) {
                                const props = data.props.pageProps;
                                if (props.content) content += props.content + '\\n';
                                if (props.description) content += props.description + '\\n';
                                if (props.body) content += props.body + '\\n';
                            }
                            
                            return content;
                        } catch (e) {
                            return '';
                        }
                    }
                    
                    // Look for Next.js app container
                    const nextRoot = document.querySelector('#__next, [data-reactroot]');
                    if (nextRoot) {
                        const unwanted = nextRoot.querySelectorAll('script, style, nav, header, footer, aside');
                        unwanted.forEach(el => el.remove());
                        return nextRoot.innerText;
                    }
                    
                    return '';
                }
            """)
            return nextjs_content
        except:
            return ""
    
    async def _extract_react_content(self, page: Page) -> str:
        """Extract content from React applications"""
        try:
            react_content = await page.evaluate("""
                () => {
                    // Look for React root containers
                    const reactSelectors = [
                        '#root',
                        '#app', 
                        '.app',
                        '[data-reactroot]',
                        '[data-react-helmet]'
                    ];
                    
                    for (const selector of reactSelectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            // Remove unwanted elements
                            const unwanted = element.querySelectorAll('script, style, nav, header, footer, aside, .sidebar');
                            unwanted.forEach(el => el.remove());
                            
                            return element.innerText;
                        }
                    }
                    return '';
                }
            """)
            return react_content
        except:
            return ""
    
    async def _extract_links_dynamic(self, page: Page, current_url: str, domain: str) -> List[str]:
        """Extract links from dynamically loaded page"""
        try:
            links = await page.evaluate("""
                (domain) => {
                    const links = Array.from(document.querySelectorAll('a[href]'));
                    const validLinks = [];
                    
                    links.forEach(link => {
                        try {
                            const href = link.href;
                            const url = new URL(href);
                            
                            // Only include links from the same domain
                            if (url.hostname === domain) {
                                // Clean up URL (remove fragments, etc.)
                                const cleanUrl = url.origin + url.pathname;
                                if (cleanUrl && !validLinks.includes(cleanUrl)) {
                                    validLinks.push(cleanUrl);
                                }
                            }
                        } catch (e) {}
                    });
                    
                    return validLinks;
                }
            """, domain)
            
            return links
            
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
            return []
    
    def _should_exclude_url(self, url: str, exclude_patterns: List[str]) -> bool:
        """Check if URL should be excluded based on patterns"""
        for pattern in exclude_patterns:
            if pattern in url:
                return True
        
        # Additional exclusions for common non-content URLs
        exclude_extensions = ['.pdf', '.jpg', '.png', '.gif', '.svg', '.css', '.js', '.xml', '.json']
        for ext in exclude_extensions:
            if url.lower().endswith(ext):
                return True
                
        return False
    
    def _should_include_url(self, url: str, include_patterns: List[str]) -> bool:
        """Check if URL should be included based on patterns"""
        for pattern in include_patterns:
            if pattern in url:
                return True
        return False
    
    def _clean_content(self, content: str) -> str:
        """Clean up extracted content"""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remove common boilerplate text
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and very short lines
            if len(line) < 3:
                continue
                
            # Skip common navigation/footer text
            skip_patterns = [
                'home', 'about', 'contact', 'privacy', 'terms',
                'cookie', 'subscribe', 'newsletter', 'follow us',
                'copyright', '©', 'all rights reserved', 'skip to',
                'menu', 'search', 'login', 'sign up', 'cart'
            ]
            
            if len(line) < 50 and any(pattern in line.lower() for pattern in skip_patterns):
                continue
            
            # Skip lines that are mostly symbols or numbers
            if len(re.sub(r'[^a-zA-Z]', '', line)) < len(line) * 0.5:
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    async def _cleanup(self):
        """Clean up browser resources"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Maintain backward compatibility
class HybridScraper(AdvancedWebScraper):
    """Backward compatible alias for AdvancedWebScraper"""
    pass
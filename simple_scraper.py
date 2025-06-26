# simple_scraper.py - HTTP fallback for anti-bot protected sites
import asyncio
import logging
import time
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SimpleHTTPScraper:
    def __init__(self):
        self.session = None
        
    async def scrape_website(self, base_url: str, max_pages: int = 50, 
                           include_patterns: List[str] = None, 
                           exclude_patterns: List[str] = None) -> List[Dict]:
        """Simple HTTP scraping as fallback"""
        
        if include_patterns is None:
            include_patterns = []
        if exclude_patterns is None:
            exclude_patterns = []
            
        logger.info(f"🌐 Starting HTTP scraping (Playwright fallback) for: {base_url}")
        
        pages_data = []
        urls_to_visit = [base_url]
        visited_urls = set()
        
        # Create HTTP client with realistic headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        try:
            async with httpx.AsyncClient(
                headers=headers,
                timeout=30.0,
                follow_redirects=True,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            ) as client:
                
                for i, url in enumerate(urls_to_visit[:max_pages]):
                    if url in visited_urls:
                        continue
                        
                    visited_urls.add(url)
                    logger.info(f"📄 HTTP Scraping ({i+1}/{min(max_pages, len(urls_to_visit))}): {url}")
                    
                    try:
                        # Make HTTP request
                        response = await client.get(url)
                        
                        if response.status_code == 403:
                            logger.warning(f"⚠️  403 Forbidden - Site may block scrapers: {url}")
                            continue
                        elif response.status_code == 429:
                            logger.warning(f"⚠️  429 Rate Limited - Waiting longer...")
                            await asyncio.sleep(random.uniform(5, 10))
                            continue
                        elif response.status_code >= 400:
                            logger.warning(f"⚠️  HTTP {response.status_code}: {url}")
                            continue
                        
                        # Parse content
                        page_data = self._parse_html_content(url, response.text)
                        
                        if page_data and page_data.get('content'):
                            pages_data.append(page_data)
                            logger.info(f"✅ Success: {len(page_data['content'])} chars extracted")
                            
                            # Extract more URLs
                            soup = BeautifulSoup(response.text, 'html.parser')
                            new_urls = self._extract_urls_from_soup(soup, base_url, include_patterns, exclude_patterns)
                            
                            for new_url in new_urls:
                                if new_url not in visited_urls and new_url not in urls_to_visit:
                                    urls_to_visit.append(new_url)
                        else:
                            logger.warning(f"⚠️  No content extracted from {url}")
                        
                        # Polite delay
                        await asyncio.sleep(random.uniform(2, 5))
                        
                    except Exception as e:
                        logger.error(f"❌ HTTP Error for {url}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"💥 HTTP scraping error: {e}")
            
        logger.info(f"🎯 HTTP scraping completed: {len(pages_data)} pages scraped")
        return pages_data
    
    def _parse_html_content(self, url: str, html: str) -> Optional[Dict]:
        """Parse HTML content using BeautifulSoup"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Get title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else ''
            
            # Try multiple content selectors
            content = ""
            content_selectors = [
                'main',
                'article', 
                '.content',
                '.main-content',
                '#content',
                '#main',
                '.container',
                'body'
            ]
            
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    # Get the largest element by text length
                    largest_element = max(elements, key=lambda x: len(x.get_text()))
                    text = largest_element.get_text(strip=True)
                    if len(text) > len(content):
                        content = text
                    if len(content) > 500:  # Good enough
                        break
            
            # Fallback to body
            if len(content) < 100:
                body = soup.find('body')
                if body:
                    content = body.get_text(strip=True)
            
            # Clean content
            content = self._clean_content(content)
            
            if not content or len(content) < 100:
                logger.warning(f"   ⚠️  Insufficient content: {len(content)} chars")
                return None
            
            # Get links
            links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                if href:
                    links.append({'href': href, 'text': text})
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'links': links,
                'scraped_at': time.time()
            }
            
        except Exception as e:
            logger.error(f"   ❌ HTML parsing error: {e}")
            return None
    
    def _clean_content(self, content: str) -> str:
        """Clean extracted content"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = ' '.join(content.split())
        
        # Remove common unwanted text
        unwanted_patterns = [
            r'Cookie Policy.*?(?=\.|$)',
            r'Privacy Policy.*?(?=\.|$)',
            r'Terms of Service.*?(?=\.|$)',
            r'All rights reserved.*?(?=\.|$)',
            r'Copyright.*?(?=\.|$)',
            r'Skip to.*?content',
            r'Menu\s*',
            r'Search\s*',
            r'Subscribe.*?(?=\.|$)',
            r'Sign up.*?(?=\.|$)',
            r'Log\s?in\s*'
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Limit length
        if len(content) > 8000:
            content = content[:8000] + "..."
        
        return content.strip()
    
    def _extract_urls_from_soup(self, soup: BeautifulSoup, base_url: str, 
                               include_patterns: List[str], exclude_patterns: List[str]) -> List[str]:
        """Extract URLs from BeautifulSoup object"""
        base_domain = urlparse(base_url).netloc
        valid_urls = []
        
        for link in soup.find_all('a', href=True):
            try:
                href = link.get('href')
                if not href:
                    continue
                
                # Convert to absolute URL
                full_url = urljoin(base_url, href)
                parsed_url = urlparse(full_url)
                
                # Skip if different domain
                if parsed_url.netloc != base_domain:
                    continue
                
                # Skip unwanted file types
                unwanted_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.css', '.js', '.xml']
                if any(full_url.lower().endswith(ext) for ext in unwanted_extensions):
                    continue
                
                # Skip unwanted paths
                unwanted_paths = ['/wp-admin', '/admin', '/login', '/register']
                if any(path in full_url.lower() for path in unwanted_paths):
                    continue
                
                # Apply filters
                if include_patterns and not any(pattern in full_url for pattern in include_patterns):
                    continue
                
                if exclude_patterns and any(pattern in full_url for pattern in exclude_patterns):
                    continue
                
                # Clean URL
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                
                if clean_url not in valid_urls:
                    valid_urls.append(clean_url)
                    
            except Exception:
                continue
        
        return valid_urls


# Updated main.py fallback
class HybridScraper:
    def __init__(self):
        self.playwright_scraper = None  # Your existing scraper
        self.http_scraper = SimpleHTTPScraper()
    
    async def scrape_website(self, base_url: str, max_pages: int = 50, 
                           include_patterns: List[str] = None, 
                           exclude_patterns: List[str] = None) -> List[Dict]:
        """Try Playwright first, fallback to HTTP"""
        
        logger.info("🚀 Attempting Playwright scraping...")
        
        # Try Playwright first (your existing scraper)
        try:
            from scraper import WebScraper  # Your enhanced scraper
            self.playwright_scraper = WebScraper()
            pages = await self.playwright_scraper.scrape_website(
                base_url, max_pages, include_patterns, exclude_patterns
            )
            
            if pages and len(pages) > 0:
                logger.info(f"✅ Playwright succeeded: {len(pages)} pages")
                return pages
            else:
                logger.warning("⚠️  Playwright got 0 pages, trying HTTP fallback...")
                
        except Exception as e:
            logger.error(f"❌ Playwright failed: {e}")
            logger.info("🔄 Falling back to simple HTTP scraping...")
        
        # Fallback to HTTP
        try:
            pages = await self.http_scraper.scrape_website(
                base_url, max_pages, include_patterns, exclude_patterns
            )
            
            if pages and len(pages) > 0:
                logger.info(f"✅ HTTP fallback succeeded: {len(pages)} pages")
                return pages
            else:
                logger.error("❌ Both Playwright and HTTP failed to get content")
                return []
                
        except Exception as e:
            logger.error(f"❌ HTTP fallback also failed: {e}")
            return []
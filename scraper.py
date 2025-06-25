import asyncio
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime

from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
import httpx

class WebScraper:
    def __init__(self):
        self.visited_urls = set()
        self.session = None
    
    async def scrape_website(
        self, 
        base_url: str, 
        max_pages: int = 50,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None
    ) -> List[Dict]:
        """Scrape website content using Playwright"""
        
        include_patterns = include_patterns or []
        exclude_patterns = exclude_patterns or []
        
        pages_data = []
        urls_to_visit = [base_url]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            try:
                while urls_to_visit and len(pages_data) < max_pages:
                    current_url = urls_to_visit.pop(0)
                    
                    if current_url in self.visited_urls:
                        continue
                    
                    # Check URL patterns
                    if not self._should_scrape_url(current_url, include_patterns, exclude_patterns):
                        continue
                    
                    page_data = await self._scrape_page(context, current_url)
                    if page_data:
                        pages_data.append(page_data)
                        self.visited_urls.add(current_url)
                        
                        # Extract new URLs
                        new_urls = self._extract_urls(page_data.get('html', ''), base_url)
                        urls_to_visit.extend(new_urls)
            
            finally:
                await browser.close()
        
        return pages_data
    
    async def _scrape_page(self, context, url: str) -> Optional[Dict]:
        """Scrape individual page content"""
        try:
            page = await context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            # Get page content
            html = await page.content()
            title = await page.title()
            
            # Extract main content using BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main'))
            
            if main_content:
                text_content = main_content.get_text(strip=True, separator=' ')
            else:
                text_content = soup.get_text(strip=True, separator=' ')
            
            # Clean text
            text_content = re.sub(r'\s+', ' ', text_content)
            text_content = text_content.strip()
            
            await page.close()
            
            return {
                'url': url,
                'title': title,
                'content': text_content,
                'html': html,
                'scraped_at': datetime.now().isoformat(),
                'word_count': len(text_content.split())
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def _should_scrape_url(self, url: str, include_patterns: List[str], exclude_patterns: List[str]) -> bool:
        """Check if URL should be scraped based on patterns"""
        
        # Check exclude patterns first
        for pattern in exclude_patterns:
            if pattern in url:
                return False
        
        # If include patterns specified, URL must match at least one
        if include_patterns:
            for pattern in include_patterns:
                if pattern in url:
                    return True
            return False
        
        return True
    
    def _extract_urls(self, html: str, base_url: str) -> List[str]:
        """Extract URLs from HTML content"""
        soup = BeautifulSoup(html, 'html.parser')
        urls = []
        base_domain = urlparse(base_url).netloc
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Only include URLs from same domain
            if urlparse(full_url).netloc == base_domain:
                urls.append(full_url)
        
        return list(set(urls))  # Remove duplicates
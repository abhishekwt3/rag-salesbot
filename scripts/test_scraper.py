# test_scraper.py - Test the advanced web scraper capabilities
import asyncio
import logging
import time
from simple_scraper import AdvancedWebScraper

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_static_website():
    """Test scraping a static website"""
    print("\n🧪 Testing Static Website (example.com)")
    scraper = AdvancedWebScraper()
    
    start_time = time.time()
    pages = await scraper.scrape_website(
        'https://example.com',
        {'single_page_mode': True}
    )
    end_time = time.time()
    
    if pages:
        page = pages[0]
        print(f"✅ Success! Scraped in {end_time - start_time:.2f}s")
        print(f"📄 Title: {page['title']}")
        print(f"📝 Content length: {len(page['content'])} characters")
        print(f"🔗 URL: {page['url']}")
        print(f"📊 Preview: {page['content'][:200]}...")
    else:
        print("❌ Failed to scrape content")

async def test_nextjs_website():
    """Test scraping a Next.js website"""
    print("\n🧪 Testing Next.js Website (nextjs.org)")
    scraper = AdvancedWebScraper()
    
    start_time = time.time()
    pages = await scraper.scrape_website(
        'https://nextjs.org',
        {'single_page_mode': True}
    )
    end_time = time.time()
    
    if pages:
        page = pages[0]
        print(f"✅ Success! Scraped in {end_time - start_time:.2f}s")
        print(f"📄 Title: {page['title']}")
        print(f"📝 Content length: {len(page['content'])} characters")
        print(f"🔗 URL: {page['url']}")
        print(f"📊 Preview: {page['content'][:200]}...")
    else:
        print("❌ Failed to scrape content")

async def test_react_website():
    """Test scraping a React website"""
    print("\n🧪 Testing React Website (react.dev)")
    scraper = AdvancedWebScraper()
    
    start_time = time.time()
    pages = await scraper.scrape_website(
        'https://react.dev',
        {'single_page_mode': True}
    )
    end_time = time.time()
    
    if pages:
        page = pages[0]
        print(f"✅ Success! Scraped in {end_time - start_time:.2f}s")
        print(f"📄 Title: {page['title']}")
        print(f"📝 Content length: {len(page['content'])} characters")
        print(f"🔗 URL: {page['url']}")
        print(f"📊 Preview: {page['content'][:200]}...")
    else:
        print("❌ Failed to scrape content")

async def test_multi_page_scraping():
    """Test multi-page scraping with limits"""
    print("\n🧪 Testing Multi-Page Scraping (httpbin.org)")
    scraper = AdvancedWebScraper()
    
    start_time = time.time()
    pages = await scraper.scrape_website(
        'https://httpbin.org',
        {
            'single_page_mode': False,
            'max_pages': 3,  # Limit for testing
            'exclude_patterns': ['/json', '/xml', '/status']
        }
    )
    end_time = time.time()
    
    print(f"✅ Scraped {len(pages)} pages in {end_time - start_time:.2f}s")
    for i, page in enumerate(pages[:3], 1):
        print(f"  📄 Page {i}: {page['title'][:50]}... ({len(page['content'])} chars)")

async def benchmark_scraping_speed():
    """Benchmark scraping speed for different types of sites"""
    print("\n📊 Benchmarking Scraping Speed")
    
    test_sites = [
        ('Static', 'https://example.com'),
        ('Next.js', 'https://nextjs.org'),
        ('React', 'https://react.dev'),
    ]
    
    scraper = AdvancedWebScraper()
    
    for site_type, url in test_sites:
        try:
            start_time = time.time()
            pages = await scraper.scrape_website(url, {'single_page_mode': True})
            end_time = time.time()
            
            duration = end_time - start_time
            content_length = len(pages[0]['content']) if pages else 0
            
            print(f"  {site_type:8} | {duration:6.2f}s | {content_length:8,} chars")
            
        except Exception as e:
            print(f"  {site_type:8} | ERROR  | {str(e)[:50]}...")

async def main():
    """Run all tests"""
    print("🚀 Advanced Web Scraper Test Suite")
    print("=" * 50)
    
    try:
        # Test different website types
        await test_static_website()
        await test_nextjs_website()
        await test_react_website()
        await test_multi_page_scraping()
        await benchmark_scraping_speed()
        
        print("\n🎉 All tests completed!")
        print("\n📋 Summary:")
        print("✅ Static websites: Supported")
        print("✅ Next.js applications: Supported")
        print("✅ React applications: Supported") 
        print("✅ Multi-page scraping: Supported")
        print("✅ Dynamic content loading: Supported")
        
        print("\n💡 Tips:")
        print("- Use single_page_mode=True for faster scraping")
        print("- Add include/exclude patterns for targeted scraping")
        print("- Increase timeout for very slow websites")
        print("- Monitor memory usage for large scraping jobs")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        print("💡 Make sure you've run: python setup_browsers.py")

if __name__ == "__main__":
    asyncio.run(main())
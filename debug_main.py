# debug_fiib_main.py - Check what's on the main FIIB website
import asyncio
import httpx
from bs4 import BeautifulSoup

async def debug_fiib_main():
    """Debug the main FIIB website"""
    
    urls_to_test = [
        "https://www.fiib.edu.in",
        "https://www.fiib.edu.in/",
        "https://fiib.edu.in",
        "https://www.fiib.edu.in/courses",
        "https://www.fiib.edu.in/admissions"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        for url in urls_to_test:
            try:
                print(f"\n🔍 Testing: {url}")
                response = await client.get(url)
                
                print(f"📊 Status: {response.status_code}")
                print(f"📊 Content Length: {len(response.text)}")
                print(f"📊 Content Type: {response.headers.get('content-type', 'Unknown')}")
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Title
                    title = soup.find('title')
                    print(f"📊 Title: {title.get_text() if title else 'No title'}")
                    
                    # Body content
                    body = soup.find('body')
                    if body:
                        body_text = body.get_text(strip=True)
                        print(f"📊 Body text length: {len(body_text)}")
                        if body_text:
                            print(f"📊 First 200 chars: '{body_text[:200]}...'")
                    
                    # Check for common elements
                    main_tag = soup.find('main')
                    article_tag = soup.find('article')
                    content_div = soup.find('div', class_=lambda x: x and 'content' in x.lower() if x else False)
                    
                    print(f"📊 Has <main>: {bool(main_tag)}")
                    print(f"📊 Has <article>: {bool(article_tag)}")
                    print(f"📊 Has content div: {bool(content_div)}")
                    
                    # Links
                    links = soup.find_all('a', href=True)
                    print(f"📊 Total links: {len(links)}")
                    
                    # Look for FIIB-specific content
                    html_lower = response.text.lower()
                    fiib_indicators = [
                        'fiib' in html_lower,
                        'fortune' in html_lower,
                        'institute' in html_lower,
                        'business' in html_lower,
                        'mba' in html_lower
                    ]
                    print(f"📊 FIIB content indicators: {sum(fiib_indicators)}/5")
                    
                else:
                    print(f"❌ Failed with status {response.status_code}")
                
            except Exception as e:
                print(f"❌ Error testing {url}: {e}")

if __name__ == "__main__":
    asyncio.run(debug_fiib_main())
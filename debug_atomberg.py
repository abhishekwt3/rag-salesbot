#!/usr/bin/env python3
"""
Simple test for atomberg.com scraping issues
"""

import asyncio
import time
import httpx
from playwright.async_api import async_playwright

async def test_http_first():
    """Test simple HTTP request first"""
    print("🌐 Testing HTTP request to atomberg.com...")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get('https://atomberg.com/', headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"   Content length: {len(response.text)} chars")
            
            if "cloudflare" in response.text.lower():
                print("   🚫 Cloudflare detected")
            if "captcha" in response.text.lower():
                print("   🤖 Captcha detected")
            if response.status_code == 403:
                print("   🛡️ Access forbidden (bot protection)")
                
            return response.status_code == 200
            
    except Exception as e:
        print(f"   ❌ HTTP failed: {e}")
        return False

async def test_playwright_quick():
    """Test Playwright with minimal timeout"""
    print("\n🎭 Testing Playwright (headless)...")
    
    playwright = await async_playwright().start()
    
    try:
        browser = await playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = await context.new_page()
        
        # Quick test - just try to load
        try:
            start = time.time()
            await page.goto('https://atomberg.com/', timeout=8000)
            load_time = time.time() - start
            
            title = await page.title()
            url = page.url
            
            print(f"   ✅ Loaded in {load_time:.1f}s")
            print(f"   Title: {title}")
            print(f"   Final URL: {url}")
            
            # Check if redirected
            if 'atomberg.com' not in url:
                print(f"   🔄 Redirected to: {url}")
                
            return True
            
        except Exception as e:
            print(f"   ❌ Playwright failed: {e}")
            return False
            
    except Exception as e:
        print(f"   💥 Browser setup failed: {e}")
        return False
        
    finally:
        try:
            await browser.close()
            await playwright.stop()
        except:
            pass

async def test_alternative_sites():
    """Test with easier sites to confirm scraper works"""
    print("\n✅ Testing with easier sites...")
    
    test_sites = [
        'https://example.com',
        'https://httpbin.org', 
        'https://google.com'
    ]
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    context = await browser.new_context()
    
    for url in test_sites:
        try:
            page = await context.new_page()
            start = time.time()
            
            await page.goto(url, timeout=5000)
            load_time = time.time() - start
            title = await page.title()
            
            print(f"   {url}: ✅ {load_time:.1f}s - {title}")
            await page.close()
            
        except Exception as e:
            print(f"   {url}: ❌ {e}")
    
    await browser.close()
    await playwright.stop()

async def main():
    print("🧪 Debugging atomberg.com scraping...\n")
    
    # Test 1: Simple HTTP
    http_works = await test_http_first()
    
    # Test 2: Playwright
    playwright_works = await test_playwright_quick()
    
    # Test 3: Other sites
    await test_alternative_sites()
    
    print(f"\n📊 Results:")
    print(f"   HTTP: {'✅' if http_works else '❌'}")
    print(f"   Playwright: {'✅' if playwright_works else '❌'}")
    
    if not http_works:
        print(f"\n💡 Suggestion: atomberg.com blocks bots. Try:")
        print(f"   - Add delays between requests")
        print(f"   - Use residential proxies")
        print(f"   - Manual content upload instead")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
Debug test for atomberg.com scraping issues
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def debug_atomberg():
    """Debug why atomberg.com fails to load"""
    
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)  # Visible browser for debugging
    
    try:
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        # Monitor network activity
        requests = []
        responses = []
        
        page.on("request", lambda req: requests.append(f"→ {req.method} {req.url}"))
        page.on("response", lambda resp: responses.append(f"← {resp.status} {resp.url}"))
        
        print("🔍 Testing atomberg.com loading...")
        start_time = time.time()
        
        try:
            # Test different loading strategies
            print("\n1. Testing basic goto...")
            await page.goto('https://atomberg.com/', timeout=10000)
            print(f"   ✅ Basic load: {time.time() - start_time:.1f}s")
            
        except Exception as e:
            print(f"   ❌ Basic load failed: {e}")
            
            try:
                print("\n2. Testing without waiting...")
                await page.goto('https://atomberg.com/', wait_until='commit', timeout=5000)
                print(f"   ✅ Commit load: {time.time() - start_time:.1f}s")
            except Exception as e2:
                print(f"   ❌ Commit load failed: {e2}")
        
        # Check what loaded
        print(f"\n📊 Network Activity:")
        print(f"   Requests: {len(requests)}")
        print(f"   Responses: {len(responses)}")
        
        if requests:
            print(f"   First 3 requests:")
            for req in requests[:3]:
                print(f"     {req}")
        
        if responses:
            print(f"   Response codes: {[r.split()[1] for r in responses[:5]]}")
        
        # Check page state
        try:
            title = await page.title()
            url = page.url
            ready_state = await page.evaluate("document.readyState")
            
            print(f"\n📄 Page State:")
            print(f"   Title: {title}")
            print(f"   URL: {url}")
            print(f"   Ready State: {ready_state}")
            
            # Check for common blocking elements
            blocking_checks = {
                "Cloudflare": "cf-browser-verification",
                "Captcha": "[data-captcha]",
                "Loading": ".loading, .spinner",
                "Error": ".error, .404"
            }
            
            for check_name, selector in blocking_checks.items():
                try:
                    element = await page.query_selector(selector)
                    if element:
                        print(f"   🚫 Found {check_name} blocker")
                    else:
                        print(f"   ✅ No {check_name} blocker")
                except:
                    print(f"   ? {check_name} check failed")
            
            # Get content sample
            try:
                content = await page.evaluate("""
                    () => {
                        const body = document.body;
                        return body ? body.innerText.substring(0, 500) : 'No body found';
                    }
                """)
                print(f"\n📝 Content Sample:")
                print(f"   {content[:200]}...")
                
            except Exception as e:
                print(f"   ❌ Content extraction failed: {e}")
        
        except Exception as e:
            print(f"❌ Page state check failed: {e}")
        
        # Wait a bit to see if anything loads
        print(f"\n⏳ Waiting 5 seconds for lazy loading...")
        await page.wait_for_timeout(5000)
        
        try:
            final_content = await page.evaluate("document.body.innerText.length")
            print(f"   📏 Final content length: {final_content} chars")
        except:
            print(f"   ❌ Could not get final content length")
            
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        
    finally:
        await browser.close()
        await playwright.stop()

if __name__ == "__main__":
    asyncio.run(debug_atomberg())
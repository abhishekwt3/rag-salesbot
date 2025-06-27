# debug_fiib_faculty.py - Debug the specific FIIB faculty page
import asyncio
import httpx
from bs4 import BeautifulSoup

async def debug_fiib_faculty_page():
    """Debug the specific FIIB faculty page that's failing"""
    
    url = "https://www.fiib.edu.in/meet-our-faculty/dr-sneha-pandey"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
            print(f"🔍 Debugging: {url}")
            
            response = await client.get(url)
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📊 Content Length: {len(response.text)} characters")
            print(f"📊 Content Type: {response.headers.get('content-type', 'Unknown')}")
            
            # Save the raw HTML for inspection
            with open('debug_fiib_faculty_raw.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"💾 Raw HTML saved to: debug_fiib_faculty_raw.html")
            
            if response.status_code == 200:
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Check title
                title = soup.find('title')
                print(f"📊 Title: {title.get_text() if title else 'No title'}")
                
                # Check body content BEFORE cleanup
                body = soup.find('body')
                if body:
                    raw_body_text = body.get_text()
                    print(f"📊 Raw body text length: {len(raw_body_text)}")
                    if raw_body_text:
                        print(f"📊 First 300 chars of raw body:")
                        print(f"'{raw_body_text[:300]}...'")
                
                # Check what's actually in the HTML
                print(f"\n🔍 HTML Analysis:")
                print(f"   - Total HTML length: {len(response.text)}")
                print(f"   - Contains 'Dr. Sneha Pandey': {'Dr. Sneha Pandey' in response.text}")
                print(f"   - Contains 'faculty': {'faculty' in response.text.lower()}")
                print(f"   - Contains 'FIIB': {'FIIB' in response.text}")
                
                # Remove scripts and styles to see what's left
                for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                    element.decompose()
                
                # Check body after cleanup
                body_after = soup.find('body')
                if body_after:
                    clean_text = body_after.get_text(strip=True)
                    print(f"\n📄 After cleanup:")
                    print(f"   - Clean text length: {len(clean_text)}")
                    if clean_text:
                        print(f"   - Clean text sample: '{clean_text[:300]}...'")
                    else:
                        print(f"   - No clean text found!")
                
                # Check for JavaScript frameworks and dynamic content indicators
                html_lower = response.text.lower()
                
                # Check for common JavaScript frameworks
                frameworks = {
                    'React': 'react' in html_lower,
                    'Vue': 'vue' in html_lower or 'vuejs' in html_lower,
                    'Angular': 'angular' in html_lower or 'ng-' in html_lower,
                    'jQuery': 'jquery' in html_lower,
                    'Next.js': 'next' in html_lower and 'js' in html_lower,
                    'Nuxt': 'nuxt' in html_lower
                }
                
                print(f"\n🔍 JavaScript Framework Detection:")
                detected_frameworks = []
                for framework, found in frameworks.items():
                    status = '✅ Found' if found else '❌ Not found'
                    print(f"   {framework}: {status}")
                    if found:
                        detected_frameworks.append(framework)
                
                # Check for dynamic loading indicators
                dynamic_indicators = [
                    'data-react', 'data-vue', '__NEXT_DATA__', 'window.__INITIAL_STATE__',
                    'loading', 'spinner', 'skeleton', 'placeholder',
                    'app.js', 'main.js', 'bundle.js', 'chunk.js'
                ]
                
                found_indicators = []
                for indicator in dynamic_indicators:
                    if indicator in html_lower:
                        found_indicators.append(indicator)
                
                print(f"\n⚡ Dynamic Content Indicators:")
                if found_indicators:
                    print(f"   Found: {', '.join(found_indicators)}")
                else:
                    print(f"   None found")
                
                # Check for specific content that should be on faculty page
                faculty_indicators = [
                    'dr. sneha pandey', 'sneha pandey', 'professor', 'faculty',
                    'department', 'education', 'experience', 'qualification'
                ]
                
                found_faculty_content = []
                for indicator in faculty_indicators:
                    if indicator in html_lower:
                        found_faculty_content.append(indicator)
                
                print(f"\n👩‍🏫 Faculty Content Indicators:")
                if found_faculty_content:
                    print(f"   Found: {', '.join(found_faculty_content)}")
                else:
                    print(f"   None found - content likely loads with JavaScript")
                
                # Check for meta tags that might have info
                meta_description = soup.find('meta', attrs={'name': 'description'})
                if meta_description:
                    description = meta_description.get('content', '')
                    print(f"\n📝 Meta Description: {description}")
                
                meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
                if meta_keywords:
                    keywords = meta_keywords.get('content', '')
                    print(f"📝 Meta Keywords: {keywords}")
                
                # Final diagnosis
                print(f"\n🎯 DIAGNOSIS:")
                if len(clean_text) < 100:
                    print(f"   ❌ PROBLEM: Very little static content ({len(clean_text)} chars)")
                    if detected_frameworks:
                        print(f"   🔍 CAUSE: Detected {', '.join(detected_frameworks)} - content loads with JavaScript")
                    print(f"   💡 SOLUTION: Use manual content addition or JavaScript rendering")
                else:
                    print(f"   ✅ Static content available: {len(clean_text)} chars")
                
                # Show what a manual content entry would look like
                print(f"\n📝 MANUAL CONTENT SUGGESTION:")
                print(f"   If this page has Dr. Sneha Pandey's info, add it manually:")
                print(f"""
   curl -X POST "http://localhost:8000/add-manual-content" \\
     -H "Content-Type: application/json" \\
     -d '{{
       "title": "Dr. Sneha Pandey - FIIB Faculty",
       "content": "Dr. Sneha Pandey is a faculty member at Fortune Institute of International Business (FIIB). She specializes in [her area]. Her educational background includes [degrees]. She has [years] of experience in [field].",
       "url": "{url}"
     }}'
                """)
                
            else:
                print(f"\n❌ HTTP Error: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

# Also test the main FIIB page for comparison
async def compare_fiib_pages():
    """Compare main page vs faculty page"""
    
    urls = [
        "https://www.fiib.edu.in/",
        "https://www.fiib.edu.in/meet-our-faculty/dr-sneha-pandey"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        for url in urls:
            try:
                print(f"\n🔍 Testing: {url}")
                response = await client.get(url)
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove scripts and styles
                for element in soup(['script', 'style']):
                    element.decompose()
                
                body = soup.find('body')
                clean_text = body.get_text(strip=True) if body else ""
                
                print(f"   Status: {response.status_code}")
                print(f"   HTML Length: {len(response.text)}")
                print(f"   Clean Text: {len(clean_text)} chars")
                print(f"   Has Faculty Keywords: {'faculty' in clean_text.lower()}")
                
            except Exception as e:
                print(f"   Error: {e}")

if __name__ == "__main__":
    print("🔍 FIIB Faculty Page Debug")
    print("=" * 50)
    
    # Run main debug
    asyncio.run(debug_fiib_faculty_page())
    
    print("\n" + "=" * 50)
    print("📊 Comparison Test")
    
    # Run comparison
    asyncio.run(compare_fiib_pages())
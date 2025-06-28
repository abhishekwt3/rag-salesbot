# setup_browsers.py - Setup script for Playwright browsers
import subprocess
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_playwright_browsers():
    """Install Playwright browsers for web scraping"""
    try:
        logger.info("🌐 Installing Playwright browsers...")
        
        # Install Chromium browser
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Chromium browser installed successfully")
        else:
            logger.error(f"❌ Failed to install Chromium: {result.stderr}")
            return False
        
        # Install browser dependencies
        logger.info("📦 Installing browser dependencies...")
        deps_result = subprocess.run([
            sys.executable, "-m", "playwright", "install-deps"
        ], capture_output=True, text=True)
        
        if deps_result.returncode == 0:
            logger.info("✅ Browser dependencies installed successfully")
        else:
            logger.warning(f"⚠️ Browser dependencies installation had issues: {deps_result.stderr}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error installing Playwright browsers: {e}")
        return False

def test_browser_installation():
    """Test if browser installation works"""
    try:
        logger.info("🧪 Testing browser installation...")
        
        # Test if playwright can launch a browser
        test_code = """
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://example.com')
        title = await page.title()
        await browser.close()
        return title

result = asyncio.run(test())
print(f"Test successful: {result}")
"""
        
        result = subprocess.run([
            sys.executable, "-c", test_code
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            logger.info("✅ Browser test successful")
            return True
        else:
            logger.error(f"❌ Browser test failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Browser test timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error testing browser: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Advanced Web Scraper...")
    
    # Install browsers
    if install_playwright_browsers():
        logger.info("✅ Browser installation completed")
    else:
        logger.error("❌ Browser installation failed")
        sys.exit(1)
    
    # Test installation
    if test_browser_installation():
        logger.info("🎉 Advanced Web Scraper setup completed successfully!")
        print("\n📋 Features enabled:")
        print("  ✅ JavaScript rendering")
        print("  ✅ Dynamic content loading")
        print("  ✅ Next.js applications")
        print("  ✅ React SPAs")
        print("  ✅ Lazy loading support")
        print("  ✅ Anti-bot detection")
    else:
        logger.error("❌ Setup test failed. Please check your installation.")
        sys.exit(1)

if __name__ == "__main__":
    main()
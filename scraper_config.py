# scraper_config.py - Configuration for different website types and scraping strategies

from typing import Dict, List

class ScrapingStrategy:
    """Configuration for different types of websites"""
    
    # Strategy for static websites (traditional HTML)
    STATIC_WEBSITE = {
        "use_javascript": False,
        "wait_for_load": False,
        "scroll_page": False,
        "timeout": 15000,
        "wait_selectors": []
    }
    
    # Strategy for SPA (Single Page Applications)
    SPA_WEBSITE = {
        "use_javascript": True,
        "wait_for_load": True,
        "scroll_page": True,
        "timeout": 30000,
        "wait_selectors": ["main", "[role='main']", ".content", "#content"]
    }
    
    # Strategy for Next.js applications
    NEXTJS_WEBSITE = {
        "use_javascript": True,
        "wait_for_load": True,
        "scroll_page": True,
        "timeout": 30000,
        "wait_for_function": "() => window.__NEXT_DATA__ || document.querySelector('[data-reactroot]')",
        "wait_selectors": ["#__next", "[data-reactroot]", "main"]
    }
    
    # Strategy for React applications
    REACT_WEBSITE = {
        "use_javascript": True,
        "wait_for_load": True,
        "scroll_page": True,
        "timeout": 30000,
        "wait_for_function": "() => window.React || document.querySelector('[data-reactroot]')",
        "wait_selectors": ["#root", "#app", "[data-reactroot]"]
    }
    
    # Strategy for e-commerce sites (with lazy loading)
    ECOMMERCE_WEBSITE = {
        "use_javascript": True,
        "wait_for_load": True,
        "scroll_page": True,
        "scroll_steps": 5,
        "timeout": 45000,
        "wait_selectors": [".product", ".products", ".catalog", ".shop"]
    }
    
    # Strategy for documentation sites
    DOCUMENTATION_WEBSITE = {
        "use_javascript": True,
        "wait_for_load": True,
        "scroll_page": False,
        "timeout": 20000,
        "wait_selectors": [".docs", ".documentation", ".guide", "article"]
    }

def detect_website_type(url: str, page_source: str = None) -> Dict:
    """
    Auto-detect website type and return appropriate scraping strategy
    
    Args:
        url: Website URL
        page_source: Optional page source for analysis
        
    Returns:
        Dictionary with scraping configuration
    """
    url_lower = url.lower()
    
    # Check for known patterns in URL
    if any(pattern in url_lower for pattern in ['shop', 'store', 'cart', 'product']):
        return ScrapingStrategy.ECOMMERCE_WEBSITE
    
    if any(pattern in url_lower for pattern in ['docs', 'documentation', 'guide', 'wiki']):
        return ScrapingStrategy.DOCUMENTATION_WEBSITE
    
    # If we have page source, analyze it
    if page_source:
        source_lower = page_source.lower()
        
        # Check for Next.js indicators
        if any(indicator in source_lower for indicator in ['__next_data__', 'next.js', '_next/']):
            return ScrapingStrategy.NEXTJS_WEBSITE
        
        # Check for React indicators
        if any(indicator in source_lower for indicator in ['react', 'data-reactroot', 'react-dom']):
            return ScrapingStrategy.REACT_WEBSITE
        
        # Check for SPA indicators
        if any(indicator in source_lower for indicator in ['spa', 'single-page', 'angular', 'vue']):
            return ScrapingStrategy.SPA_WEBSITE
    
    # Default to SPA strategy for modern websites
    return ScrapingStrategy.SPA_WEBSITE

# Website-specific configurations
WEBSITE_CONFIGS = {
    # Popular website patterns
    "nextjs.org": ScrapingStrategy.NEXTJS_WEBSITE,
    "react.dev": ScrapingStrategy.REACT_WEBSITE,
    "docs.": ScrapingStrategy.DOCUMENTATION_WEBSITE,
    "shopify": ScrapingStrategy.ECOMMERCE_WEBSITE,
    "woocommerce": ScrapingStrategy.ECOMMERCE_WEBSITE,
    
    # Common SaaS platforms
    "vercel.com": ScrapingStrategy.NEXTJS_WEBSITE,
    "netlify.com": ScrapingStrategy.SPA_WEBSITE,
    "github.io": ScrapingStrategy.SPA_WEBSITE,
    
    # Documentation sites
    "gitbook": ScrapingStrategy.DOCUMENTATION_WEBSITE,
    "notion.site": ScrapingStrategy.SPA_WEBSITE,
    "confluence": ScrapingStrategy.SPA_WEBSITE,
}

def get_config_for_url(url: str) -> Dict:
    """Get scraping configuration for a specific URL"""
    url_lower = url.lower()
    
    # Check for specific website configurations
    for pattern, config in WEBSITE_CONFIGS.items():
        if pattern in url_lower:
            return config
    
    # Auto-detect based on URL patterns
    return detect_website_type(url)

# Content extraction priorities for different website types
CONTENT_SELECTORS = {
    "primary": [
        "main",
        "[role='main']",
        ".main-content",
        "#main-content",
        "article",
        ".content",
        "#content"
    ],
    "secondary": [
        ".post-content",
        ".entry-content",
        ".page-content",
        ".article-content",
        ".prose",
        ".markdown-body"
    ],
    "nextjs": [
        "#__next",
        "[data-reactroot]",
        ".next-app"
    ],
    "react": [
        "#root",
        "#app",
        ".app",
        "[data-reactroot]"
    ],
    "documentation": [
        ".docs",
        ".documentation",
        ".guide",
        ".tutorial",
        ".api-docs"
    ],
    "ecommerce": [
        ".product-description",
        ".product-details",
        ".product-info",
        ".item-details"
    ]
}

# Selectors to exclude from content extraction
EXCLUDE_SELECTORS = [
    "script",
    "style", 
    "nav",
    "header", 
    "footer",
    "aside",
    ".navigation",
    ".menu",
    ".sidebar",
    ".ad",
    ".advertisement",
    ".cookie-banner",
    ".newsletter",
    ".popup",
    ".modal",
    ".comments",
    ".related-posts"
]
# app.py - ULTRA FAST version with simple text similarity (no external APIs for embeddings!)
import os
import asyncio
import logging
import json
import math
import re
from typing import List, Dict, Optional, Set
from datetime import datetime
from urllib.parse import urljoin, urlparse
from collections import Counter
import time

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn

# Simple imports that always work
import httpx
import tiktoken
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ultra Fast RAG Chatbot API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class WebsiteConfig(BaseModel):
    url: HttpUrl
    max_pages: int = 50
    include_patterns: List[str] = []
    exclude_patterns: List[str] = ["/blog", "/news"]

class QueryRequest(BaseModel):
    question: str
    max_results: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float

# Ultra Fast Text Similarity Vector Store
class UltraFastVectorStore:
    def __init__(self):
        self.chunks = []
        self.chunk_vectors = []  # Simple word frequency vectors
        self.vocabulary = set()  # All unique words
        self.ready = False
        self.last_updated = None
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Simple text preprocessing"""
        # Convert to lowercase and extract words
        text = text.lower()
        # Remove punctuation and split
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'this', 'that', 'these', 'those'}
        words = [w for w in words if w not in stop_words and len(w) > 2]
        return words
    
    def _create_vector(self, words: List[str]) -> Dict[str, int]:
        """Create simple word frequency vector"""
        return Counter(words)
    
    async def process_pages(self, pages: List[Dict]):
        """ULTRA FAST processing with simple text similarity"""
        logger.info(f"⚡ ULTRA FAST processing starting for {len(pages)} pages...")
        start_total = time.time()
        
        # Create chunks (fast)
        logger.info("📝 Step 1: Creating chunks...")
        start_chunks = time.time()
        all_chunks = []
        
        for i, page in enumerate(pages):
            try:
                chunks = self._create_chunks(page)
                all_chunks.extend(chunks)
                logger.info(f"   📄 Page {i+1}/{len(pages)}: {len(chunks)} chunks ({page.get('title', 'Untitled')[:50]})")
            except Exception as e:
                logger.error(f"   ❌ Error with page {i+1}: {e}")
                continue
        
        chunks_time = time.time() - start_chunks
        logger.info(f"✅ Created {len(all_chunks)} chunks in {chunks_time:.2f}s")
        
        if not all_chunks:
            logger.error("❌ No chunks created!")
            return
        
        # Create vocabulary and vectors (super fast)
        logger.info("🔤 Step 2: Building vocabulary...")
        start_vocab = time.time()
        
        all_words = set()
        chunk_word_lists = []
        
        for i, chunk in enumerate(all_chunks):
            words = self._preprocess_text(chunk['text'])
            chunk_word_lists.append(words)
            all_words.update(words)
            
            if (i + 1) % 10 == 0:
                logger.info(f"   📊 Processed {i+1}/{len(all_chunks)} chunks for vocabulary")
        
        self.vocabulary = all_words
        vocab_time = time.time() - start_vocab
        logger.info(f"✅ Built vocabulary of {len(self.vocabulary)} words in {vocab_time:.2f}s")
        
        # Create vectors (very fast)
        logger.info("🧮 Step 3: Creating similarity vectors...")
        start_vectors = time.time()
        
        self.chunks = all_chunks
        self.chunk_vectors = []
        
        for i, words in enumerate(chunk_word_lists):
            vector = self._create_vector(words)
            self.chunk_vectors.append(vector)
            
            if (i + 1) % 20 == 0:
                logger.info(f"   ⚡ Created {i+1}/{len(all_chunks)} vectors")
        
        vectors_time = time.time() - start_vectors
        logger.info(f"✅ Created vectors in {vectors_time:.2f}s")
        
        # Finalize
        self.ready = True
        self.last_updated = datetime.now().isoformat()
        self._save_to_file()
        
        total_time = time.time() - start_total
        logger.info(f"🎉 ULTRA FAST processing completed in {total_time:.2f}s total!")
        logger.info(f"📊 Knowledge base ready: {len(self.chunks)} chunks, {len(self.vocabulary)} unique words")
    
    def _create_chunks(self, page: Dict) -> List[Dict]:
        """Create chunks from page content"""
        try:
            content = page.get('content', '')
            if not content or len(content) < 100:
                return []
            
            # Simple sentence-based chunking for better semantic coherence
            sentences = re.split(r'[.!?]+', content)
            
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                # If adding this sentence would make chunk too long, save current chunk
                if len(current_chunk) + len(sentence) > 1000:
                    if current_chunk:
                        chunks.append({
                            'text': current_chunk.strip(),
                            'metadata': {
                                'source_url': page.get('url', ''),
                                'title': page.get('title', ''),
                                'chunk_index': len(chunks),
                                'scraped_at': page.get('scraped_at', '')
                            }
                        })
                    current_chunk = sentence
                else:
                    current_chunk += " " + sentence
            
            # Add final chunk
            if current_chunk.strip():
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': {
                        'source_url': page.get('url', ''),
                        'title': page.get('title', ''),
                        'chunk_index': len(chunks),
                        'scraped_at': page.get('scraped_at', '')
                    }
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks: {e}")
            return []
    
    async def search_similar(self, query: str, max_results: int = 5) -> List[Dict]:
        """ULTRA FAST similarity search"""
        if not self.ready:
            self._load_from_file()
        
        if not self.chunks:
            return []
        
        try:
            # Preprocess query
            query_words = self._preprocess_text(query)
            query_vector = self._create_vector(query_words)
            
            # Calculate similarities (very fast)
            similarities = []
            for i, chunk_vector in enumerate(self.chunk_vectors):
                similarity = self._cosine_similarity_fast(query_vector, chunk_vector)
                similarities.append({
                    'index': i,
                    'similarity': similarity,
                    'chunk': self.chunks[i]
                })
            
            # Sort and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            results = []
            for item in similarities[:max_results]:
                results.append({
                    'text': item['chunk']['text'],
                    'metadata': item['chunk']['metadata'],
                    'score': item['similarity']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            return []
    
    def _cosine_similarity_fast(self, vec1: Dict[str, int], vec2: Dict[str, int]) -> float:
        """Fast cosine similarity for word frequency vectors"""
        try:
            # Get intersection of words
            common_words = set(vec1.keys()) & set(vec2.keys())
            
            if not common_words:
                return 0.0
            
            # Calculate dot product
            dot_product = sum(vec1[word] * vec2[word] for word in common_words)
            
            # Calculate magnitudes
            mag1 = math.sqrt(sum(count * count for count in vec1.values()))
            mag2 = math.sqrt(sum(count * count for count in vec2.values()))
            
            if mag1 == 0 or mag2 == 0:
                return 0.0
            
            return dot_product / (mag1 * mag2)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0
    
    def _save_to_file(self):
        """Save to JSON file"""
        try:
            data = {
                'chunks': self.chunks,
                'chunk_vectors': [dict(vector) for vector in self.chunk_vectors],  # Convert Counter to dict
                'vocabulary': list(self.vocabulary),
                'last_updated': self.last_updated,
                'ready': self.ready
            }
            with open('vector_store.json', 'w') as f:
                json.dump(data, f)
            logger.info(f"💾 Saved {len(self.chunks)} chunks to file")
        except Exception as e:
            logger.error(f"Error saving to file: {e}")
    
    def _load_from_file(self):
        """Load from JSON file"""
        try:
            with open('vector_store.json', 'r') as f:
                data = json.load(f)
                self.chunks = data.get('chunks', [])
                self.chunk_vectors = [Counter(vector) for vector in data.get('chunk_vectors', [])]
                self.vocabulary = set(data.get('vocabulary', []))
                self.last_updated = data.get('last_updated')
                self.ready = data.get('ready', False) and len(self.chunks) > 0
            logger.info(f"📁 Loaded {len(self.chunks)} chunks from file")
        except FileNotFoundError:
            logger.info("📁 No existing vector store file found")
        except Exception as e:
            logger.error(f"Error loading from file: {e}")
    
    def is_ready(self) -> bool:
        if not self.ready:
            self._load_from_file()
        return self.ready
    
    def get_total_chunks(self) -> int:
        return len(self.chunks)

# Simple web scraper with progress
class SimpleWebScraper:
    def __init__(self):
        self.visited_urls = set()
    
    async def scrape_website(self, base_url: str, max_pages: int = 50, 
                           include_patterns: List[str] = None,
                           exclude_patterns: List[str] = None) -> List[Dict]:
        """Scrape website with detailed progress"""
        include_patterns = include_patterns or []
        exclude_patterns = exclude_patterns or []
        
        pages_data = []
        urls_to_visit = [base_url]
        
        logger.info(f"🌐 Starting to scrape {base_url}")
        logger.info(f"📊 Target: {max_pages} pages maximum")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            
            try:
                while urls_to_visit and len(pages_data) < max_pages:
                    current_url = urls_to_visit.pop(0)
                    
                    if current_url in self.visited_urls:
                        continue
                    
                    if not self._should_scrape_url(current_url, include_patterns, exclude_patterns):
                        continue
                    
                    logger.info(f"🔄 Scraping ({len(pages_data)+1}/{max_pages}): {current_url}")
                    page_data = await self._scrape_page(context, current_url)
                    
                    if page_data:
                        pages_data.append(page_data)
                        self.visited_urls.add(current_url)
                        logger.info(f"✅ Success: {len(page_data['content'])} chars, '{page_data['title'][:50]}'")
                        
                        # Extract new URLs
                        new_urls = self._extract_urls(page_data.get('html', ''), base_url)
                        urls_to_visit.extend(new_urls)
                    else:
                        logger.warning(f"⚠️  Skipped: No content extracted")
            
            finally:
                await browser.close()
        
        logger.info(f"🎯 Scraping completed: {len(pages_data)} pages scraped")
        return pages_data
    
    async def _scrape_page(self, context, url: str) -> Optional[Dict]:
        """Scrape single page"""
        try:
            page = await context.new_page()
            await page.goto(url, wait_until='networkidle', timeout=30000)
            
            html = await page.content()
            title = await page.title()
            
            # Extract text content
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content'))
            
            if main_content:
                text_content = main_content.get_text(strip=True, separator=' ')
            else:
                text_content = soup.get_text(strip=True, separator=' ')
            
            # Clean text
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            await page.close()
            
            if len(text_content) < 100:
                return None
            
            return {
                'url': url,
                'title': title,
                'content': text_content,
                'html': html,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            return None
    
    def _should_scrape_url(self, url: str, include_patterns: List[str], exclude_patterns: List[str]) -> bool:
        """Check if URL should be scraped"""
        for pattern in exclude_patterns:
            if pattern in url:
                return False
        
        if include_patterns:
            for pattern in include_patterns:
                if pattern in url:
                    return True
            return False
        
        return True
    
    def _extract_urls(self, html: str, base_url: str) -> List[str]:
        """Extract URLs from HTML"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            urls = []
            base_domain = urlparse(base_url).netloc
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                
                if urlparse(full_url).netloc == base_domain:
                    urls.append(full_url)
            
            return list(set(urls))
        except Exception as e:
            logger.error(f"Error extracting URLs: {e}")
            return []

# Gemini Chat Manager (same as before)
class GeminiChatManager:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            logger.error("GOOGLE_API_KEY not found in environment")
    
    async def process_query(self, question: str, max_results: int = 5) -> Dict:
        """Process user query using Gemini 2.0 Flash"""
        logger.info(f"🔍 Processing query: '{question[:50]}...'")
        
        # Get relevant context
        context_results = await self.vector_store.search_similar(question, max_results)
        
        if not context_results:
            return {
                "answer": "I don't have information about that topic in my knowledge base.",
                "sources": [],
                "confidence": 0.0
            }
        
        logger.info(f"📚 Found {len(context_results)} relevant chunks")
        
        # Build context
        context_text = "\n\n".join([
            f"Source: {result['metadata']['source_url']}\n{result['text']}"
            for result in context_results
        ])
        
        # Generate response using Gemini 2.0 Flash
        try:
            prompt = f"""You are a helpful sales assistant for this company's website. Answer questions based ONLY on the provided context from the company's website.

Focus on sales, pricing, and product information. If the information is not in the context, clearly say you don't have that information. Keep responses concise and helpful.

Context from company website:
{context_text}

Question: {question}

Please provide a helpful answer based on the context above."""

            logger.info("🤖 Generating response with Gemini...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.google_api_key}",
                    headers={
                        "Content-Type": "application/json"
                    },
                    json={
                        "contents": [
                            {
                                "parts": [
                                    {
                                        "text": prompt
                                    }
                                ]
                            }
                        ],
                        "generationConfig": {
                            "temperature": 0.1,
                            "maxOutputTokens": 500,
                            "topP": 0.8,
                            "topK": 10
                        }
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                    raise Exception(f"Gemini API error: {response.status_code}")
                
                data = response.json()
                
                # Extract answer from Gemini response
                if 'candidates' in data and len(data['candidates']) > 0:
                    answer = data['candidates'][0]['content']['parts'][0]['text']
                    logger.info("✅ Response generated successfully")
                else:
                    raise Exception("No response from Gemini")
                
                # Calculate confidence
                avg_confidence = sum(result['score'] for result in context_results) / len(context_results)
                
                # Format sources
                sources = [
                    {
                        "url": result['metadata']['source_url'],
                        "title": result['metadata']['title'],
                        "relevance_score": round(result['score'], 3)
                    }
                    for result in context_results
                ]
                
                return {
                    "answer": answer,
                    "sources": sources,
                    "confidence": round(avg_confidence, 3)
                }
                
        except Exception as e:
            logger.error(f"Error generating response with Gemini: {e}")
            return {
                "answer": "Sorry, I encountered an error processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0
            }

# Global instances
vector_store = UltraFastVectorStore()
scraper = SimpleWebScraper()
chat_manager = GeminiChatManager(vector_store)

# API Routes
@app.post("/setup-website")
async def setup_website(config: WebsiteConfig, background_tasks: BackgroundTasks):
    """Setup website scraping"""
    background_tasks.add_task(process_website, str(config.url), config.max_pages, config.include_patterns, config.exclude_patterns)
    return {"message": "Website processing started", "status": "processing"}

@app.post("/query", response_model=QueryResponse)
async def query_chatbot(request: QueryRequest):
    """Process query"""
    if not vector_store.is_ready():
        raise HTTPException(status_code=400, detail="Knowledge base not ready")
    
    response = await chat_manager.process_query(request.question, request.max_results)
    return QueryResponse(**response)

@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "ready" if vector_store.is_ready() else "not_ready",
        "total_chunks": vector_store.get_total_chunks(),
        "last_updated": vector_store.last_updated
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

async def process_website(url: str, max_pages: int, include_patterns: List[str], exclude_patterns: List[str]):
    """Background website processing with detailed progress"""
    try:
        logger.info(f"🚀 ULTRA FAST processing starting for: {url}")
        total_start = time.time()
        
        # Scrape website
        pages = await scraper.scrape_website(url, max_pages, include_patterns, exclude_patterns)
        
        if not pages:
            logger.error("❌ No pages scraped! Check the URL and try again.")
            return
        
        # Process with ultra fast method
        await vector_store.process_pages(pages)
        
        total_time = time.time() - total_start
        
        if vector_store.is_ready():
            logger.info(f"🎉 COMPLETE! Total time: {total_time:.2f}s")
            logger.info(f"📊 Ready to answer questions about {url}")
        else:
            logger.error("❌ Processing failed")
            
    except Exception as e:
        logger.error(f"💥 Website processing error: {e}")

if __name__ == "__main__":
    # Only need Google API key for chat!
    if not os.getenv('GOOGLE_API_KEY'):
        print("❌ ERROR: Please set GOOGLE_API_KEY environment variable")
        print("Get it from: https://makersuite.google.com/app/apikey")
        exit(1)
    
    print("⚡ Starting ULTRA FAST RAG Chatbot API...")
    print("🚀 No external APIs needed for embeddings - uses simple text similarity!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
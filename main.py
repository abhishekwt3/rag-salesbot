# main.py - Fixed version with no duplicates and working single page mode
import os
import asyncio
import logging
import time
from typing import List, Dict
from datetime import datetime

# Load .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn

# Import the vector store
from fast_embeddings import FastSentenceTransformerStore
from simple_scraper import HybridScraper as WebScraper

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fast Semantic RAG Chatbot API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models - FIXED: Only one WebsiteConfig definition
class WebsiteConfig(BaseModel):
    url: HttpUrl
    max_pages: int = 50
    include_patterns: List[str] = []
    exclude_patterns: List[str] = ["/blog", "/news"]
    single_page_mode: bool = False

class QueryRequest(BaseModel):
    question: str
    max_results: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float

class ManualContent(BaseModel):
    title: str
    content: str
    url: str = "manual://added"

# Chat Manager for Semantic Search
class SemanticChatManager:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            logger.error("GOOGLE_API_KEY not found in environment")
    
    async def process_query(self, question: str, max_results: int = 5) -> Dict:
        """Process user query using semantic search + Gemini"""
        logger.info(f"🔍 Processing semantic query: '{question[:50]}...'")
        
        # Get semantically relevant context
        context_results = await self.vector_store.search_similar(question, max_results)
        
        if not context_results:
            return {
                "answer": "I don't have information about that topic in my knowledge base.",
                "sources": [],
                "confidence": 0.0
            }
        
        logger.info(f"📚 Found {len(context_results)} semantically relevant chunks")
        logger.info(f"🎯 Top relevance score: {context_results[0]['score']:.3f}")
        
        # Build context with better semantic understanding
        context_text = "\n\n".join([
            f"Source: {result['metadata']['source_url']}\nRelevance: {result['score']:.3f}\nContent: {result['text']}"
            for result in context_results
        ])
        
        # Enhanced prompt for semantic understanding
        try:
            prompt = f"""You are a knowledgeable sales assistant with semantic understanding of this company's website. 

The following context has been semantically matched to the user's question (with relevance scores):

Context from company website:
{context_text}

User Question: {question}

Instructions:
- Answer based on the semantically relevant context above
- Focus on sales, pricing, and product information
- If information isn't in the context, clearly state that
- Use the relevance scores to prioritize information
- Provide clear, helpful answers that demonstrate understanding

Answer:"""

            logger.info("🤖 Generating semantic response with Gemini...")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.google_api_key}",
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": prompt}]}],
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
                
                if 'candidates' in data and len(data['candidates']) > 0:
                    answer = data['candidates'][0]['content']['parts'][0]['text']
                    logger.info("✅ Semantic response generated successfully")
                else:
                    raise Exception("No response from Gemini")
                
                # Calculate semantic confidence
                avg_confidence = sum(result['score'] for result in context_results) / len(context_results)
                
                # Format sources with semantic scores
                sources = [
                    {
                        "url": result['metadata']['source_url'],
                        "title": result['metadata']['title'],
                        "semantic_score": round(result['score'], 3),
                        "relevance": "High" if result['score'] > 0.7 else "Medium" if result['score'] > 0.5 else "Low"
                    }
                    for result in context_results
                ]
                
                return {
                    "answer": answer,
                    "sources": sources,
                    "confidence": round(avg_confidence, 3)
                }
                
        except Exception as e:
            logger.error(f"Error generating semantic response: {e}")
            return {
                "answer": "Sorry, I encountered an error processing your question. Please try again.",
                "sources": [],
                "confidence": 0.0
            }

# Global instances
vector_store = FastSentenceTransformerStore(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
scraper = WebScraper()
chat_manager = SemanticChatManager(vector_store)

# FIXED: Only ONE setup-website endpoint with single_page_mode support
@app.post("/setup-website")
async def setup_website(config: WebsiteConfig, background_tasks: BackgroundTasks):
    """Setup website scraping with optional single page mode"""
    
    mode_desc = "single page" if config.single_page_mode else f"up to {config.max_pages} pages"
    logger.info(f"🚀 Starting website processing: {config.url} ({mode_desc})")
    
    background_tasks.add_task(
        process_website, 
        str(config.url), 
        config.max_pages, 
        config.include_patterns, 
        config.exclude_patterns,
        config.single_page_mode
    )
    
    return {
        "message": f"Website processing started for {config.url}",
        "mode": "single_page" if config.single_page_mode else "multi_page",
        "max_pages": 1 if config.single_page_mode else config.max_pages,
        "status": "processing"
    }

# Single page endpoint
@app.post("/scrape-single-page")
async def scrape_single_page(config: WebsiteConfig, background_tasks: BackgroundTasks):
    """🎯 SINGLE PAGE MODE - Scrape ONLY the given URL, no crawling"""
    logger.info(f"🎯 Single Page Mode: {config.url}")
    
    background_tasks.add_task(
        process_single_page, 
        str(config.url)
    )
    
    return {
        "message": f"Single page scraping started for {config.url}",
        "mode": "single_page_only",
        "status": "processing"
    }

@app.post("/query", response_model=QueryResponse)
async def query_chatbot(request: QueryRequest):
    """Process semantic query"""
    if not vector_store.is_ready():
        raise HTTPException(status_code=400, detail="Semantic knowledge base not ready")
    
    response = await chat_manager.process_query(request.question, request.max_results)
    return QueryResponse(**response)

@app.get("/status")
async def get_status():
    """Get semantic system status"""
    return {
        "status": "ready" if vector_store.is_ready() else "not_ready",
        "total_chunks": vector_store.get_total_chunks(),
        "last_updated": vector_store.last_updated,
        "search_type": "semantic_sentence_transformers",
        "model": vector_store.model_name
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/add-manual-content")
async def add_manual_content(content: ManualContent):
    """Add content manually when scraping is blocked"""
    try:
        page_data = {
            'url': content.url,
            'title': content.title,
            'content': content.content,
            'links': [],
            'scraped_at': time.time()
        }
        
        logger.info(f"📝 Adding manual content: {content.title}")
        await vector_store.process_pages([page_data])
        
        return {
            "message": f"Manual content '{content.title}' added successfully",
            "chunks_created": vector_store.get_total_chunks(),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error adding manual content: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add content: {str(e)}")

@app.get("/clear-knowledge-base")
async def clear_knowledge_base():
    """Clear the knowledge base for fresh start"""
    try:
        global vector_store
        vector_store = FastSentenceTransformerStore(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        return {
            "message": "Knowledge base cleared successfully",
            "status": "cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear: {str(e)}")

# FIXED: Single page processing function
async def process_single_page(url: str):
    """Process only the single page - FIXED to work with HybridScraper"""
    try:
        logger.info(f"🎯 Processing SINGLE PAGE ONLY: {url}")
        
        # FIXED: HybridScraper doesn't support single_page_mode parameter
        # So we call it normally but only process one page
        pages = await scraper.scrape_website(
            url, 
            max_pages=1,  # Only scrape 1 page
            include_patterns=[], 
            exclude_patterns=[]
            # Remove single_page_mode parameter - not supported by HybridScraper
        )
        
        if pages:
            await vector_store.process_pages(pages)
            logger.info(f"✅ Single page processed: {url}")
            logger.info(f"📊 Extracted {len(pages[0]['content'])} characters")
        else:
            logger.error(f"❌ Failed to extract content from: {url}")
            
    except Exception as e:
        logger.error(f"💥 Single page processing error: {e}")

# Background processing function
async def process_website(url: str, max_pages: int, include_patterns: List[str], 
                         exclude_patterns: List[str], single_page_mode: bool = False):
    """Background website processing with single page mode support"""
    try:
        mode_desc = "single page" if single_page_mode else f"multi-page (max {max_pages})"
        logger.info(f"🚀 Processing {url} in {mode_desc} mode")
        
        total_start = time.time()
        
        # FIXED: Handle single page mode by adjusting parameters
        if single_page_mode:
            # For single page mode, only scrape 1 page
            pages = await scraper.scrape_website(url, 1, [], [])
        else:
            # For multi-page mode, use all parameters
            pages = await scraper.scrape_website(url, max_pages, include_patterns, exclude_patterns)
        
        if not pages:
            logger.error("❌ No pages scraped! Check the URL and try again.")
            return
        
        # Process pages into vector store
        await vector_store.process_pages(pages)
        
        total_time = time.time() - total_start
        
        if vector_store.is_ready():
            logger.info(f"🎉 Processing completed in {total_time:.2f}s")
            logger.info(f"📊 Processed {len(pages)} pages from {url}")
            logger.info(f"🔍 Mode: {mode_desc}")
            logger.info(f"💾 Total chunks in knowledge base: {vector_store.get_total_chunks()}")
        else:
            logger.error("❌ Processing failed")
            
    except Exception as e:
        logger.error(f"💥 Website processing error: {e}")

if __name__ == "__main__":
    # Check environment
    google_api_key = os.getenv('GOOGLE_API_KEY')
    
    if not google_api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found!")
        print("🔍 Debugging .env file...")
        
        env_file_path = ".env"
        if os.path.exists(env_file_path):
            print(f"✅ .env file exists at: {os.path.abspath(env_file_path)}")
            
            try:
                with open(env_file_path, 'r') as f:
                    lines = f.readlines()
                print(f"📄 .env file has {len(lines)} lines")
                
                google_line_found = False
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith('GOOGLE_API_KEY'):
                        google_line_found = True
                        masked_line = line.split('=')[0] + '=***HIDDEN***'
                        print(f"   Line {i}: {masked_line}")
                        break
                
                if not google_line_found:
                    print("❌ No GOOGLE_API_KEY line found in .env file")
                    print("📝 Add this line to your .env file:")
                    print("GOOGLE_API_KEY=your_actual_api_key_here")
                else:
                    print("⚠️  GOOGLE_API_KEY line exists but not loading properly")
                    
            except Exception as e:
                print(f"❌ Error reading .env file: {e}")
        else:
            print(f"❌ .env file not found at: {os.path.abspath(env_file_path)}")
            print("📝 Create a .env file with:")
            print("GOOGLE_API_KEY=your_actual_api_key_here")
        
        print("\n🔗 Get your API key from: https://makersuite.google.com/app/apikey")
        exit(1)
    else:
        print(f"✅ GOOGLE_API_KEY loaded successfully (ending: ...{google_api_key[-6:]})")
    
    print("🚀 Starting RAG Chatbot API...")
    print("🎯 Single Page Mode: Available")
    print("🌐 Multi-Page Mode: Available")
    uvicorn.run(app, host="0.0.0.0", port=8000)
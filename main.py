# main.py - Updated with Fast Sentence Transformers
import os
import asyncio
import logging
import time
from typing import List, Dict
from datetime import datetime

# ADD THIS AT THE TOP - Load .env file
from dotenv import load_dotenv
load_dotenv()  # This loads the .env file

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import uvicorn

# Import the new fast sentence transformer store
from fast_embeddings import FastSentenceTransformerStore
#from scraper import WebScraper  # Keep existing scraper If using semantic search
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

# Pydantic models (same as before)
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

# Updated Chat Manager for Semantic Search
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
                
                # Calculate semantic confidence (higher scores = better semantic match)
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

# Global instances - NOW WITH SEMANTIC SEARCH!
vector_store = FastSentenceTransformerStore(
    model_name="sentence-transformers/all-MiniLM-L6-v2"  # Fast semantic model
)
scraper = WebScraper()  # Keep existing scraper
chat_manager = SemanticChatManager(vector_store)

# API Routes (same as before)
@app.post("/setup-website")
async def setup_website(config: WebsiteConfig, background_tasks: BackgroundTasks):
    """Setup website scraping with semantic processing"""
    background_tasks.add_task(process_website, str(config.url), config.max_pages, config.include_patterns, config.exclude_patterns)
    return {"message": "Website processing started with semantic embeddings", "status": "processing"}

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

async def process_website(url: str, max_pages: int, include_patterns: List[str], exclude_patterns: List[str]):
    """Background website processing with semantic embeddings"""
    try:
        logger.info(f"🚀 SEMANTIC processing starting for: {url}")
        total_start = time.time()
        
        # Scrape website (same as before)
        pages = await scraper.scrape_website(url, max_pages, include_patterns, exclude_patterns)
        
        if not pages:
            logger.error("❌ No pages scraped! Check the URL and try again.")
            return
        
        # Process with FAST sentence transformers + FAISS
        await vector_store.process_pages(pages)
        
        total_time = time.time() - total_start
        
        if vector_store.is_ready():
            logger.info(f"🎉 SEMANTIC SEARCH READY! Total time: {total_time:.2f}s")
            logger.info(f"📊 Ready for semantic queries about {url}")
        else:
            logger.error("❌ Semantic processing failed")
            
    except Exception as e:
        logger.error(f"💥 Semantic processing error: {e}")

# Add this to your main.py after the existing endpoints

class ManualContent(BaseModel):
    title: str
    content: str
    url: str = "manual://added"

@app.post("/add-manual-content")
async def add_manual_content(content: ManualContent):
    """Add content manually when scraping is blocked"""
    
    try:
        # Create manual page data
        page_data = {
            'url': content.url,
            'title': content.title,
            'content': content.content,
            'links': [],
            'scraped_at': time.time()
        }
        
        logger.info(f"📝 Adding manual content: {content.title}")
        
        # Process with your vector store
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
        # Reset the vector store
        global vector_store
        vector_store = UltraFastVectorStore()  # or FastSentenceTransformerStore() if using semantic
        
        return {
            "message": "Knowledge base cleared successfully",
            "status": "cleared"
        }
    except Exception as e:
        logger.error(f"Error clearing knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear: {str(e)}")



if __name__ == "__main__":
    # Check if .env was loaded properly
    google_api_key = os.getenv('GOOGLE_API_KEY')
    
    if not google_api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found!")
        print("🔍 Debugging .env file...")
        
        # Check if .env file exists
        env_file_path = ".env"
        if os.path.exists(env_file_path):
            print(f"✅ .env file exists at: {os.path.abspath(env_file_path)}")
            
            # Show .env file contents (safely)
            try:
                with open(env_file_path, 'r') as f:
                    lines = f.readlines()
                print(f"📄 .env file has {len(lines)} lines")
                
                # Check for GOOGLE_API_KEY line
                google_line_found = False
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith('GOOGLE_API_KEY'):
                        google_line_found = True
                        # Hide the actual key for security
                        masked_line = line.split('=')[0] + '=***HIDDEN***'
                        print(f"   Line {i}: {masked_line}")
                        break
                
                if not google_line_found:
                    print("❌ No GOOGLE_API_KEY line found in .env file")
                    print("📝 Add this line to your .env file:")
                    print("GOOGLE_API_KEY=your_actual_api_key_here")
                else:
                    print("⚠️  GOOGLE_API_KEY line exists but not loading properly")
                    print("🔧 Check for:")
                    print("   - No spaces around the = sign")
                    print("   - No quotes around the value")
                    print("   - No # comments on the same line")
                    
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
    uvicorn.run(app, host="0.0.0.0", port=8000)
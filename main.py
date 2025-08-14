# main.py - SaaS Multi-tenant RAG Chatbot API (Enhanced Scraper)
import os
import logging
from typing import List
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import docx
import time as time_module

# Load .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, RedirectResponse
from typing import List, Dict
import uvicorn
import uuid

# Import database models and utilities
from models import User, KnowledgeBase, ChatWidget, WidgetConversation, get_db, init_database
from auth import get_current_user, hash_password, create_access_token, authenticate_user
from schemas import (
    UserCreate, UserLogin, Token, 
    KnowledgeBaseCreate,
    WebsiteConfig, ProcessingResponse,
    QueryRequest, QueryResponse,
    MessageResponse, ChatWidgetCreate, ChatWidgetResponse, ChatWidgetUpdate,
    WidgetChatRequest, WidgetChatResponse, WidgetConfigResponse, DocumentUploadResponse
)
from sqlalchemy.orm import Session

# Import the enhanced vector store and scraper
from saas_embeddings import MemcacheS3VectorStore
from simple_scraper import EnhancedSimpleScraper as WebScraper

# Import Google OAuth
from google_oauth import GoogleOAuth, get_google_oauth_endpoints

import httpx

def validate_environment():
    """Validate required environment variables"""
    required_vars = [
        'QDRANT_URL',
        'GOOGLE_API_KEY'
    ]
    
    optional_vars = [
        'QDRANT_API_KEY'  # Optional for local Qdrant
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing required environment variables: {missing_vars}")
        logger.warning("Some features may not work properly")
    
    # Log optional variables
    for var in optional_vars:
        if not os.getenv(var):
            logger.info(f"Optional environment variable not set: {var}")
    
    return len(missing_vars) == 0

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate environment and initialize database
validate_environment()
init_database()

app = FastAPI(title="SaaS RAG Chatbot API", version="4.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enhanced Vector store manager with scraper integration
class SaaSVectorManager:
    def __init__(self):
        self.vector_stores = {}  # user_id -> knowledge_base_id -> vector_store
        # Initialize enhanced scraper with optimized settings
        self.scraper = WebScraper(
            max_retries=3,
            host_max_concurrent=2,  # Conservative for shared hosting
            host_min_interval_ms=500,  # Slower for politeness
            respect_robots=True,
            enable_resource_blocking=True,  # 3-5x performance boost
            on_result=self._on_scrape_result
        )
        
    def _on_scrape_result(self, tenant_id: str, page):
        """Callback when a page is successfully scraped"""
        logger.info(f"📄 Scraped: {page.final_url} ({page.framework}, {page.to_dict()['word_count']} words) for {tenant_id}")
        
    def get_vector_store(self, user_id: str, knowledge_base_id: str) -> MemcacheS3VectorStore:
        if user_id not in self.vector_stores:
            self.vector_stores[user_id] = {}
        
        if knowledge_base_id not in self.vector_stores[user_id]:
            self.vector_stores[user_id][knowledge_base_id] = MemcacheS3VectorStore(
                user_id=user_id,
                knowledge_base_id=knowledge_base_id
            )
        
        return self.vector_stores[user_id][knowledge_base_id]
    
    def clear_vector_store(self, user_id: str, knowledge_base_id: str):
        """Clear a specific vector store"""
        if user_id in self.vector_stores:
            if knowledge_base_id in self.vector_stores[user_id]:
                # Clear the vector store data
                self.vector_stores[user_id][knowledge_base_id].clear_data()
                # Remove from memory
                del self.vector_stores[user_id][knowledge_base_id]
    
    async def scrape_websites(self, jobs: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Enhanced multi-tenant website scraping
        jobs: [{"tenant_id": "user_id:kb_id", "urls": [...]}]
        returns: {tenant_id: [page_dict, ...]}
        """
        return await self.scraper.scrape_multi_tenant(jobs)

# Initialize vector manager
vector_manager = SaaSVectorManager()

# Google OAuth setup
google_oauth = GoogleOAuth()
oauth_endpoints = get_google_oauth_endpoints()

# Health check
@app.get("/")
async def root():
    return {"message": "Salesdok Assistant API is running", "version": "4.1.0", "scraper": "enhanced", "vector_db": "weaviate"}

@app.get("/health")
async def health():
    return {"status": "healthy", "scraper_features": ["multi-tenant", "spa-support", "resource-blocking", "robots-txt"]}

# Auth endpoints
@app.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    logger.info(f"New user registered: {user_data.email}")
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(user_data.email, user_data.password, db)
    
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is disabled")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    
    logger.info(f"User logged in: {user_data.email}")
    
    return {"access_token": access_token, "token_type": "bearer"}

# Google OAuth endpoints (unchanged)
@app.get("/auth/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    if not os.getenv("GOOGLE_CLIENT_ID"):
        raise HTTPException(status_code=501, detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.")
    
    auth_url = google_oauth.get_auth_url()
    return RedirectResponse(url=auth_url)

@app.get("/auth/google/callback")
async def google_callback(
    code: str = Query(...),
    state: str = Query(None),
    error: str = Query(None),
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    
    if error:
        logger.error(f"Google OAuth error: {error}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}?error=oauth_error")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    try:
        # Exchange code for token
        token_data = await google_oauth.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info from Google
        user_info = await google_oauth.get_user_info(access_token)
        
        email = user_info.get("email")
        name = user_info.get("name", "")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        
        if existing_user:
            user = existing_user
            logger.info(f"Existing user logged in via Google: {email}")
        else:
            # Create new user
            user = User(
                email=email,
                full_name=name,
                hashed_password="oauth_user",
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"New user created via Google OAuth: {email}")
        
        # Create JWT token
        jwt_token = create_access_token(data={"sub": str(user.id)})
        
        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(
            url=f"{frontend_url}?token={jwt_token}&email={email}&name={name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}?error=oauth_failed")

@app.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "created_at": current_user.created_at
    }

# Knowledge base endpoints
@app.post("/knowledge-bases")
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    knowledge_base = KnowledgeBase(
        user_id=current_user.id,
        name=kb_data.name,
        description=kb_data.description
    )
    db.add(knowledge_base)
    db.commit()
    db.refresh(knowledge_base)
    
    logger.info(f"Knowledge base created: {kb_data.name} for user {current_user.email}")
    
    return {
        "id": str(knowledge_base.id),
        "name": knowledge_base.name,
        "description": knowledge_base.description,
        "status": knowledge_base.status,
        "created_at": knowledge_base.created_at
    }

@app.get("/knowledge-bases")
async def list_knowledge_bases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    knowledge_bases = db.query(KnowledgeBase).filter(
        KnowledgeBase.user_id == current_user.id
    ).all()
    
    return [
        {
            "id": str(kb.id),
            "name": kb.name,
            "description": kb.description,
            "status": kb.status,
            "total_chunks": kb.total_chunks,
            "last_updated": kb.last_updated,
            "created_at": kb.created_at
        }
        for kb in knowledge_bases
    ]

@app.delete("/knowledge-bases/{knowledge_base_id}")
async def delete_knowledge_base(
    knowledge_base_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership
    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_base_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    # Clear vector store in Weaviate
    vector_manager.clear_vector_store(str(current_user.id), knowledge_base_id)
    
    db.delete(knowledge_base)
    db.commit()
    
    logger.info(f"Knowledge base deleted: {knowledge_base.name}")
    
    return MessageResponse(message="Knowledge base deleted successfully")

# Enhanced content processing endpoints
@app.post("/knowledge-bases/{knowledge_base_id}/process-website")
async def process_website(
    knowledge_base_id: str,
    config: WebsiteConfig,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership
    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_base_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    # Update status to processing
    knowledge_base.status = "processing"
    knowledge_base.website_url = str(config.url)
    db.commit()
    
    # Add background task with enhanced scraper
    background_tasks.add_task(
        process_website_background_enhanced,
        str(current_user.id),
        knowledge_base_id,
        config
    )
    
    logger.info(f"🚀 Enhanced website processing started for KB {knowledge_base_id}: {config.url}")
    
    return ProcessingResponse(
        message="Enhanced website processing started with SPA support",
        knowledge_base_id=knowledge_base_id,
        status="processing"
    )

async def process_website_background_enhanced(user_id: str, knowledge_base_id: str, config: WebsiteConfig):
    """Enhanced background task to process website content with multi-tenant scraper"""
    from models import SessionLocal
    db = SessionLocal()
    try:
        # Get vector store for this user and knowledge base
        vector_store = vector_manager.get_vector_store(user_id, knowledge_base_id)
        
        # Prepare URLs for scraping (support multiple URLs if provided)
        urls = []
        main_url = str(config.url)
        urls.append(main_url)
        
        # If additional URLs are provided in config, add them
        if hasattr(config, 'additional_urls') and config.additional_urls:
            urls.extend([str(url) for url in config.additional_urls])
        
        # Create multi-tenant job for enhanced scraper
        tenant_id = f"{user_id}:{knowledge_base_id}"
        scraping_jobs = [{
            "tenant_id": tenant_id,
            "urls": urls
        }]
        
        logger.info(f"🔍 Starting enhanced scraping for {len(urls)} URLs...")
        
        # Scrape using enhanced multi-tenant scraper
        results = await vector_manager.scrape_websites(scraping_jobs)
        pages = results.get(tenant_id, [])
        
        if not pages:
            logger.warning(f"⚠️ No pages scraped for KB {knowledge_base_id}")
            # Update status to error
            kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
            if kb:
                kb.status = "error"
                db.commit()
            return
        
        logger.info(f"✅ Successfully scraped {len(pages)} pages")
        
        # Convert enhanced scraper format to vector store format
        processed_pages = []
        for page_dict in pages:
            # Enhanced page format - convert to expected format for process_pages
            processed_page = {
                "url": page_dict["final_url"],
                "title": page_dict.get("title", ""),
                "content": page_dict.get("text", ""),  # This is the key field for process_pages
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                # Add enhanced metadata for logging but keep compatible format
                "framework": page_dict.get("framework", "unknown"),
                "word_count": page_dict.get("word_count", 0),
                "content_hash": page_dict.get("hash", ""),
                "status": page_dict.get("status", 200),
                **page_dict.get("meta", {})
            }
            
            # Only add pages with meaningful content
            if processed_page["content"] and len(processed_page["content"].strip()) > 50:
                processed_pages.append(processed_page)
                logger.info(f"📄 Processed: {page_dict['final_url']} ({page_dict.get('framework', 'unknown')}, {page_dict.get('word_count', 0)} words)")
                logger.debug(f"   Content preview: {processed_page['content'][:200]}...")
            else:
                logger.warning(f"⚠️ Skipping page with insufficient content: {page_dict['final_url']} (content length: {len(processed_page['content'].strip()) if processed_page['content'] else 0})")
        
        if not processed_pages:
            logger.error("❌ No valid pages with content to process")
            # Update status to error
            kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
            if kb:
                kb.status = "error"
                db.commit()
            return
        
        # Process pages through vector store using the original method
        logger.info(f"🔄 Processing {len(processed_pages)} pages through vector store...")
        await vector_store.process_pages(processed_pages)
        total_chunks = vector_store.get_total_chunks()
        
        logger.info(f"✅ Vector store processing complete: {total_chunks} chunks created")
        
        # Verify vector store is ready
        if not vector_store.is_ready():
            logger.error("❌ Vector store is not ready after processing!")
            # Update status to error
            kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
            if kb:
                kb.status = "error"
                db.commit()
            return
        
        # Update knowledge base status
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
        if kb:
            kb.status = "ready"
            kb.total_chunks = total_chunks
            kb.last_updated = datetime.now(timezone.utc)
            db.commit()
        
        logger.info(f"🎯 Enhanced website processing completed for KB {knowledge_base_id}: {len(processed_pages)} pages, {total_chunks} chunks")
        
    except Exception as e:
        logger.error(f"❌ Error in enhanced website processing for KB {knowledge_base_id}: {e}")
        # Update status to error
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
        if kb:
            kb.status = "error"
            db.commit()
    finally:
        db.close()

# Backward compatibility: Keep old function name as alias
async def process_website_background(user_id: str, knowledge_base_id: str, config: WebsiteConfig):
    """Backward compatibility wrapper"""
    await process_website_background_enhanced(user_id, knowledge_base_id, config)

# Chat endpoints (unchanged)
@app.post("/chat/query", response_model=QueryResponse)
async def query_knowledge_base(
    query: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership
    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == query.knowledge_base_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    if knowledge_base.status != "ready":
        raise HTTPException(status_code=400, detail="Knowledge base is not ready")
    
    # Get vector store
    vector_store = vector_manager.get_vector_store(str(current_user.id), query.knowledge_base_id)
    
    if not vector_store.is_ready():
        raise HTTPException(status_code=400, detail="Vector store not ready")
    
    # Process query
    try:
        result = await vector_store.process_query(query.question, query.max_results)
        
        logger.info(f"Query processed for user {current_user.email}, KB {knowledge_base.name}")
        
        return QueryResponse(
            answer=result["answer"],
            sources=result.get("sources", []),
            confidence=result.get("confidence", 0.0)
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Error processing query")

@app.get("/knowledge-bases/{knowledge_base_id}/status")
async def get_knowledge_base_status(
    knowledge_base_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_base_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    return {
        "status": knowledge_base.status,
        "total_chunks": knowledge_base.total_chunks,
        "last_updated": knowledge_base.last_updated,
        "scraper_version": "enhanced_v4.1"
    }

# Widget helper function
def widget_to_response(widget: ChatWidget) -> dict:
    """Convert a ChatWidget database object to response format"""
    return {
        "id": widget.id,
        "name": widget.name,
        "knowledge_base_id": widget.knowledge_base_id,
        "widget_key": widget.widget_key,
        "website_url": widget.website_url,
        "primary_color": widget.primary_color,
        "widget_position": widget.widget_position,
        "welcome_message": widget.welcome_message,
        "placeholder_text": widget.placeholder_text,
        "widget_title": widget.widget_title,
        "is_active": widget.is_active,
        "show_branding": widget.show_branding,
        "allowed_domains": widget.allowed_domains,
        "total_conversations": widget.total_conversations,
        "total_messages": widget.total_messages,
        "last_used": widget.last_used.isoformat() if widget.last_used else None,
        "created_at": widget.created_at.isoformat() if widget.created_at else None,
    }

# Widget management endpoints (unchanged)
@app.post("/widgets", response_model=ChatWidgetResponse)
async def create_widget(
    widget_data: ChatWidgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify ownership of knowledge base
    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == widget_data.knowledge_base_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    # Create widget
    widget = ChatWidget(
        user_id=current_user.id,
        knowledge_base_id=widget_data.knowledge_base_id,
        name=widget_data.name,
        website_url=widget_data.website_url,
        primary_color=widget_data.primary_color,
        widget_position=widget_data.widget_position,
        welcome_message=widget_data.welcome_message,
        placeholder_text=widget_data.placeholder_text,
        widget_title=widget_data.widget_title,
        show_branding=widget_data.show_branding,
        allowed_domains=','.join(widget_data.allowed_domains) if widget_data.allowed_domains else None
    )
    
    db.add(widget)
    db.commit()
    db.refresh(widget)
    
    logger.info(f"Widget created: {widget_data.name} for user {current_user.email}")
    
    return ChatWidgetResponse(**widget_to_response(widget))

@app.get("/widgets", response_model=List[ChatWidgetResponse])
async def list_widgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    widgets = db.query(ChatWidget).filter(
        ChatWidget.user_id == current_user.id
    ).all()
    
    return [ChatWidgetResponse(**widget_to_response(widget)) for widget in widgets]

@app.get("/widgets/{widget_id}", response_model=ChatWidgetResponse)
async def get_widget(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    widget = db.query(ChatWidget).filter(
        ChatWidget.id == widget_id,
        ChatWidget.user_id == current_user.id
    ).first()
    
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    return ChatWidgetResponse(**widget_to_response(widget))

@app.put("/widgets/{widget_id}", response_model=ChatWidgetResponse)
async def update_widget(
    widget_id: str,
    widget_data: ChatWidgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    widget = db.query(ChatWidget).filter(
        ChatWidget.id == widget_id,
        ChatWidget.user_id == current_user.id
    ).first()
    
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    # Update fields
    for field, value in widget_data.dict(exclude_unset=True).items():
        if field == 'allowed_domains' and value is not None:
            setattr(widget, field, ','.join(value))
        else:
            setattr(widget, field, value)

    widget.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(widget)
    
    return ChatWidgetResponse(**widget_to_response(widget))

@app.delete("/widgets/{widget_id}")
async def delete_widget(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    widget = db.query(ChatWidget).filter(
        ChatWidget.id == widget_id,
        ChatWidget.user_id == current_user.id
    ).first()
    
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    # Delete associated conversations
    db.query(WidgetConversation).filter(WidgetConversation.widget_id == widget_id).delete()
    
    db.delete(widget)
    db.commit()
    
    return MessageResponse(message="Widget deleted successfully")

# Public widget endpoints (unchanged)
@app.get("/widget/{widget_key}/config", response_model=WidgetConfigResponse)
async def get_widget_config(widget_key: str, db: Session = Depends(get_db)):
    widget = db.query(ChatWidget).filter(
        ChatWidget.widget_key == widget_key,
        ChatWidget.is_active == True
    ).first()
    
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found or inactive")
    
    return WidgetConfigResponse(
        widget_key=widget.widget_key,
        primary_color=widget.primary_color,
        widget_position=widget.widget_position,
        welcome_message=widget.welcome_message,
        placeholder_text=widget.placeholder_text,
        widget_title=widget.widget_title,
        show_branding=widget.show_branding,
        is_active=widget.is_active
    )

@app.post("/widget/{widget_key}/chat", response_model=WidgetChatResponse)
async def widget_chat(
    widget_key: str,
    chat_request: WidgetChatRequest,
    db: Session = Depends(get_db)
):
    start_time = time_module.time()
    
    # Get widget
    widget = db.query(ChatWidget).filter(
        ChatWidget.widget_key == widget_key,
        ChatWidget.is_active == True
    ).first()
    
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found or inactive")
    
    # Generate session ID if not provided
    session_id = chat_request.session_id or str(uuid.uuid4())
    
    # Get vector store and process query
    try:
        vector_store = vector_manager.get_vector_store(widget.user_id, widget.knowledge_base_id)
        
        if not vector_store.is_ready():
            raise HTTPException(status_code=400, detail="Knowledge base not ready")
        
        result = await vector_store.process_query(chat_request.message, 5)
        
        # Log conversation
        conversation = WidgetConversation(
            widget_id=widget.id,
            session_id=session_id,
            user_message=chat_request.message,
            bot_response=result["answer"],
            confidence_score=result.get("confidence", 0.0),
            response_time_ms=int((time_module.time() - start_time) * 1000),
            user_ip=None,
            user_agent='',
            referrer_url=''
        )
        
        db.add(conversation)
        
        # Update widget analytics
        widget.total_messages += 1
        widget.last_used = datetime.now(timezone.utc)

        db.commit()
        
        return WidgetChatResponse(
            response=result["answer"],
            session_id=session_id,
            confidence=result.get("confidence", 0.0),
            sources=result.get("sources", [])
        )
        
    except Exception as e:
        logger.error(f"Error in widget chat: {e}")
        raise HTTPException(status_code=500, detail="Error processing message")

# Widget JavaScript endpoint (unchanged)
@app.get("/widget/{widget_key}/script.js")
async def get_widget_script(widget_key: str, db: Session = Depends(get_db)):
    widget = db.query(ChatWidget).filter(
        ChatWidget.widget_key == widget_key,
        ChatWidget.is_active == True
    ).first()
    
    if not widget:
        raise HTTPException(status_code=404, detail="Widget not found")
    
    # Generate the JavaScript widget code
    script = f"""
// AI Chatbot Widget - Generated for {widget.name} (Enhanced Scraper v4.1)
(function() {{
    var WIDGET_CONFIG = {{
        widgetKey: '{widget.widget_key}',
        apiUrl: '{os.getenv("WIDGET_API_URL", "http://localhost:8000")}',
        primaryColor: '{widget.primary_color}',
        position: '{widget.widget_position}',
        welcomeMessage: '{widget.welcome_message}',
        placeholderText: '{widget.placeholder_text}',
        title: '{widget.widget_title}',
        showBranding: {str(widget.show_branding).lower()},
        version: '4.1-enhanced'
    }};
    
    // Load widget CSS and JS
    var link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = WIDGET_CONFIG.apiUrl + '/static/widget.css';
    document.head.appendChild(link);
    
    var script = document.createElement('script');
    script.src = WIDGET_CONFIG.apiUrl + '/static/widget.js';
    script.onload = function() {{
        if (window.initChatWidget) {{
            window.initChatWidget(WIDGET_CONFIG);
        }}
    }};
    document.head.appendChild(script);
}})();
"""
    
    return Response(content=script, media_type="application/javascript")

# Document upload endpoints (unchanged for brevity - same as original)
@app.post("/knowledge-bases/{knowledge_base_id}/upload-documents", response_model=DocumentUploadResponse)
async def upload_documents(
    knowledge_base_id: str,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and process documents (TXT, DOCX) for a knowledge base"""
    
    # Verify ownership
    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_base_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    # Validate file types
    allowed_extensions = {'.txt', '.docx', '.doc'}
    file_data = []
    
    for file in files:
        if not file.filename:
            continue
            
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            continue
            
        # Check file size (max 10MB per file)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB limit
            continue
        
        # Store file data for background processing
        file_data.append({
            'filename': file.filename,
            'content': content,
            'file_ext': file_ext
        })
    
    if not file_data:
        raise HTTPException(
            status_code=400, 
            detail="No valid files found. Please upload TXT or DOCX files (max 10MB each)"
        )
    
    # Update status to processing
    knowledge_base.status = "processing"
    db.commit()
    
    # Process files in background
    background_tasks.add_task(
        process_documents_background,
        str(current_user.id),
        knowledge_base_id,
        file_data
    )
    
    logger.info(f"Document processing started for KB {knowledge_base_id}: {len(file_data)} files")
    
    return DocumentUploadResponse(
        message=f"Processing {len(file_data)} documents",
        knowledge_base_id=knowledge_base_id,
        status="processing",
        files_processed=0,
        total_chunks_added=0
    )

async def process_documents_background(user_id: str, knowledge_base_id: str, file_data: List[Dict]):
    """Background task to process uploaded documents"""
    from models import SessionLocal
    db = SessionLocal()
    
    # Use Docker temp directory
    temp_dir = os.environ.get('TMPDIR', '/app/tmp')
    
    try:
        # Get vector store for this user and knowledge base
        vector_store = vector_manager.get_vector_store(user_id, knowledge_base_id)
        processed_files = 0
        total_chunks_added = 0
        
        for file_info in file_data:
            try:
                # Create temp file in proper directory
                temp_file_path = os.path.join(temp_dir, f"upload_{os.getpid()}_{file_info['filename']}")
                
                # Write file content
                with open(temp_file_path, 'wb') as temp_file:
                    temp_file.write(file_info['content'])
                
                # Extract text based on file type
                text_content = extract_text_from_file(temp_file_path, file_info['filename'])
                
                if text_content.strip():
                    # Create document data for processing
                    document_data = {
                        "text": text_content,
                        "metadata": {
                            "source_url": f"uploaded_file://{file_info['filename']}",
                            "title": file_info['filename'],
                            "file_type": file_info['file_ext'],
                            "uploaded_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                    
                    # Process through vector store
                    chunks_added = await vector_store.process_document(document_data)
                    total_chunks_added += chunks_added
                    processed_files += 1
                    
                    logger.info(f"Processed document {file_info['filename']}: {chunks_added} chunks added")
                
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                
            except Exception as e:
                logger.error(f"Error processing file {file_info['filename']}: {e}")
                # Clean up temp file if it exists
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    try:
                        os.unlink(temp_file_path)
                    except:
                        pass
                continue
        
        # Update knowledge base status
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
        if kb:
            kb.status = "ready" if processed_files > 0 else "error"
            kb.total_chunks = vector_store.get_total_chunks()
            kb.last_updated = datetime.now(timezone.utc)
            db.commit()
        
        logger.info(f"Document processing completed for KB {knowledge_base_id}: {processed_files} files, {total_chunks_added} chunks")
        
    except Exception as e:
        logger.error(f"Error processing documents for KB {knowledge_base_id}: {e}")
        # Update status to error
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
        if kb:
            kb.status = "error"
            db.commit()
    finally:
        db.close()

def extract_text_from_file(file_path: str, filename: str) -> str:
    """Extract text content from various file types"""
    file_ext = Path(filename).suffix.lower()
    
    try:
        if file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
        elif file_ext in ['.docx', '.doc']:
            try:
                doc = docx.Document(file_path)
                text_content = []
                
                # Extract text from paragraphs
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        text_content.append(paragraph.text.strip())
                
                # Extract text from tables
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            if cell.text.strip():
                                text_content.append(cell.text.strip())
                
                return '\n\n'.join(text_content)
                
            except Exception as e:
                logger.error(f"Error processing Word document {filename}: {e}")
                return ""
        
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            return ""
            
    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {e}")
        return ""

@app.get("/knowledge-bases/{knowledge_base_id}/processing-status")
async def get_processing_status(
    knowledge_base_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current processing status of a knowledge base"""
    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_base_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    return {
        "status": knowledge_base.status,
        "files_processed": 0,  # Could track this in database if needed
        "total_chunks_added": knowledge_base.total_chunks,
        "error_message": None if knowledge_base.status != "error" else "Processing failed",
        "scraper_version": "enhanced_v4.1"
    }

# Serve static widget files
@app.get("/static/{file_path:path}")
async def serve_static(file_path: str):
    """Serve static widget files"""
    from fastapi.responses import FileResponse
    import os
    
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    file_location = os.path.join(static_dir, file_path)
    
    if os.path.exists(file_location):
        return FileResponse(file_location)
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
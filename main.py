# main.py - SaaS Multi-tenant RAG Chatbot API
import os
import asyncio
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path

# Load .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import database models and utilities
from models import User, KnowledgeBase, get_db, init_database
from auth import get_current_user, hash_password, create_access_token, authenticate_user
from schemas import (
    UserCreate, UserLogin, Token, UserResponse,
    KnowledgeBaseCreate, KnowledgeBaseResponse, KnowledgeBaseStatus,
    WebsiteConfig, ProcessingResponse,
    QueryRequest, QueryResponse,
    MessageResponse
)
from sqlalchemy.orm import Session

# Import the vector store and scraper
from saas_embeddings import SaaSVectorStore
from simple_scraper import HybridScraper as WebScraper

import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database
init_database()

app = FastAPI(title="SaaS RAG Chatbot API", version="3.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vector store manager for multi-tenant support
class SaaSVectorManager:
    def __init__(self):
        self.vector_stores = {}  # user_id -> knowledge_base_id -> vector_store
        
    def get_vector_store(self, user_id: str, knowledge_base_id: str) -> SaaSVectorStore:
        if user_id not in self.vector_stores:
            self.vector_stores[user_id] = {}
        
        if knowledge_base_id not in self.vector_stores[user_id]:
            # Create user-specific storage directory
            storage_dir = Path(f"data/{user_id}/{knowledge_base_id}")
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            self.vector_stores[user_id][knowledge_base_id] = SaaSVectorStore(
                storage_dir=str(storage_dir)
            )
        
        return self.vector_stores[user_id][knowledge_base_id]

vector_manager = SaaSVectorManager()

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
    # Clear the database first
    knowledge_base = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == knowledge_base_id,
        KnowledgeBase.user_id == current_user.id
    ).first()
    
    if not knowledge_base:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    
    # Clear vector store files
    storage_dir = Path(f"data/{current_user.id}/{knowledge_base_id}")
    if storage_dir.exists():
        import shutil
        shutil.rmtree(storage_dir)
    
    # Remove from memory
    user_id = str(current_user.id)
    if user_id in vector_manager.vector_stores:
        if knowledge_base_id in vector_manager.vector_stores[user_id]:
            del vector_manager.vector_stores[user_id][knowledge_base_id]
    
    db.delete(knowledge_base)
    db.commit()
    
    logger.info(f"Knowledge base deleted: {knowledge_base.name}")
    
    return MessageResponse(message="Knowledge base deleted successfully")

# Content processing endpoints
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
    
    # Add background task
    background_tasks.add_task(
        process_website_background,
        str(current_user.id),
        knowledge_base_id,
        config
    )
    
    logger.info(f"Website processing started for KB {knowledge_base_id}: {config.url}")
    
    return ProcessingResponse(
        message="Website processing started",
        knowledge_base_id=knowledge_base_id,
        status="processing"
    )

async def process_website_background(user_id: str, knowledge_base_id: str, config: WebsiteConfig):
    """Background task to process website content"""
    from models import SessionLocal
    db = SessionLocal()
    try:
        # Get vector store for this user and knowledge base
        vector_store = vector_manager.get_vector_store(user_id, knowledge_base_id)
        
        # Scrape website
        scraper = WebScraper()
        pages = await scraper.scrape_website(str(config.url), config.dict())
        
        if not pages:
            # Update status to error
            kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
            if kb:
                kb.status = "error"
                db.commit()
            return
        
        # Process pages through vector store
        await vector_store.process_pages(pages)
        
        # Update knowledge base status
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
        if kb:
            kb.status = "ready"
            kb.total_chunks = vector_store.get_total_chunks()
            kb.last_updated = datetime.utcnow()
            db.commit()
        
        logger.info(f"Website processing completed for KB {knowledge_base_id}")
        
    except Exception as e:
        logger.error(f"Error processing website for KB {knowledge_base_id}: {e}")
        # Update status to error
        kb = db.query(KnowledgeBase).filter(KnowledgeBase.id == knowledge_base_id).first()
        if kb:
            kb.status = "error"
            db.commit()
    finally:
        db.close()

# Chat endpoints
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
        "last_updated": knowledge_base.last_updated
    }

# Health check
@app.get("/")
async def root():
    return {"message": "SaaS RAG Chatbot API is running", "version": "3.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
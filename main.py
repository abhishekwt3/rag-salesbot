# main.py - SaaS Multi-tenant RAG Chatbot API
import os
import asyncio
import logging
import time
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import docx

# Load .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from typing import List
import uvicorn
import uuid

# Import database models and utilities
from models import User, KnowledgeBase, ChatWidget, WidgetConversation, get_db, init_database
from auth import get_current_user, hash_password, create_access_token, authenticate_user
from schemas import (
    UserCreate, UserLogin, Token, UserResponse,
    KnowledgeBaseCreate, KnowledgeBaseResponse, KnowledgeBaseStatus,
    WebsiteConfig, ProcessingResponse,
    QueryRequest, QueryResponse,
    MessageResponse, ChatWidgetCreate, ChatWidgetResponse, ChatWidgetUpdate,
    WidgetChatRequest, WidgetChatResponse, WidgetConfigResponse, DocumentUploadResponse
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

#Widget helper function
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

# Widget management endpoints
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
    
    widget.updated_at = datetime.utcnow()
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

# Public widget endpoints (no authentication required)
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
    import time as time_module
    from fastapi import Request
    
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
            user_ip=None,  # Simplified for demo
            user_agent='',
            referrer_url=''
        )
        
        db.add(conversation)
        
        # Update widget analytics
        widget.total_messages += 1
        widget.last_used = datetime.utcnow()
        
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

# Widget JavaScript endpoint
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
// AI Chatbot Widget - Generated for {widget.name}
(function() {{
    var WIDGET_CONFIG = {{
        widgetKey: '{widget.widget_key}',
        apiUrl: '{os.getenv("WIDGET_API_URL", "http://localhost:8000")}',
        primaryColor: '{widget.primary_color}',
        position: '{widget.widget_position}',
        welcomeMessage: '{widget.welcome_message}',
        placeholderText: '{widget.placeholder_text}',
        title: '{widget.widget_title}',
        showBranding: {str(widget.show_branding).lower()}
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

# Add these endpoints to your main.py

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
    valid_files = []
    
    for file in files:
        if not file.filename:
            continue
            
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            continue
            
        # Check file size (max 10MB per file)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Seek back to beginning
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            continue
            
        valid_files.append(file)
    
    if not valid_files:
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
        valid_files
    )
    
    logger.info(f"Document processing started for KB {knowledge_base_id}: {len(valid_files)} files")
    
    return DocumentUploadResponse(
        message=f"Processing {len(valid_files)} documents",
        knowledge_base_id=knowledge_base_id,
        status="processing",
        files_processed=0,
        total_chunks_added=0
    )

async def process_documents_background(user_id: str, knowledge_base_id: str, files: List[UploadFile]):
    """Background task to process uploaded documents"""
    from models import SessionLocal
    db = SessionLocal()
    
    try:
        # Get vector store for this user and knowledge base
        vector_store = vector_manager.get_vector_store(user_id, knowledge_base_id)
        
        processed_files = 0
        total_chunks_added = 0
        
        for file in files:
            try:
                # Create temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as temp_file:
                    # Copy uploaded file content to temp file
                    content = await file.read()
                    temp_file.write(content)
                    temp_file_path = temp_file.name
                
                # Extract text based on file type
                text_content = extract_text_from_file(temp_file_path, file.filename)
                
                if text_content.strip():
                    # Create document data for processing
                    document_data = {
                        "text": text_content,
                        "metadata": {
                            "source_url": f"uploaded_file://{file.filename}",
                            "title": file.filename,
                            "file_type": Path(file.filename).suffix.lower(),
                            "uploaded_at": datetime.utcnow().isoformat()
                        }
                    }
                    
                    # Process through vector store
                    chunks_added = await vector_store.process_document(document_data)
                    total_chunks_added += chunks_added
                    processed_files += 1
                    
                    logger.info(f"Processed document {file.filename}: {chunks_added} chunks added")
                
                # Clean up temp file
                os.unlink(temp_file_path)
                
            except Exception as e:
                logger.error(f"Error processing file {file.filename}: {e}")
                # Clean up temp file if it exists
                if 'temp_file_path' in locals():
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
            kb.last_updated = datetime.utcnow()
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
            # Handle TXT files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
                
        elif file_ext in ['.docx', '.doc']:
            # Handle Word documents
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
    
    return DocumentProcessingStatus(
        status=knowledge_base.status,
        files_processed=0,  # You could track this in the database if needed
        total_chunks_added=knowledge_base.total_chunks,
        error_message=None if knowledge_base.status != "error" else "Processing failed"
    )

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

# Health check
@app.get("/")
async def root():
    return {"message": "SaaS RAG Chatbot API is running", "version": "3.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
# schemas.py - Pydantic models for API request/response schemas
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, EmailStr

# Authentication schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    created_at: str
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Knowledge Base schemas
class KnowledgeBaseCreate(BaseModel):
    name: str
    description: Optional[str] = None

class KnowledgeBaseResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    status: str
    total_chunks: int
    last_updated: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True

class KnowledgeBaseStatus(BaseModel):
    status: str
    total_chunks: int
    last_updated: Optional[str] = None

# Website processing schemas
class WebsiteConfig(BaseModel):
    url: HttpUrl
    max_pages: int = 50
    include_patterns: List[str] = []
    exclude_patterns: List[str] = ["/blog", "/news"]
    single_page_mode: bool = False

class ProcessingResponse(BaseModel):
    message: str
    knowledge_base_id: str
    status: str

# Chat schemas
class QueryRequest(BaseModel):
    question: str
    knowledge_base_id: str
    max_results: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float

# General response schemas
class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

# Widget schemas
class ChatWidgetCreate(BaseModel):
    name: str
    knowledge_base_id: str
    website_url: Optional[str] = None
    primary_color: Optional[str] = "#2563eb"
    widget_position: Optional[str] = "bottom-right"
    welcome_message: Optional[str] = "Hi! How can I help you today?"
    placeholder_text: Optional[str] = "Type your message..."
    widget_title: Optional[str] = "Chat Support"
    show_branding: Optional[bool] = True
    allowed_domains: Optional[List[str]] = []

class ChatWidgetResponse(BaseModel):
    id: str
    name: str
    knowledge_base_id: str
    widget_key: str
    website_url: Optional[str] = None
    primary_color: str
    widget_position: str
    welcome_message: str
    placeholder_text: str
    widget_title: str
    is_active: bool
    show_branding: bool
    allowed_domains: Optional[str] = None
    total_conversations: int
    total_messages: int
    last_used: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True

class ChatWidgetUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    primary_color: Optional[str] = None
    widget_position: Optional[str] = None
    welcome_message: Optional[str] = None
    placeholder_text: Optional[str] = None
    widget_title: Optional[str] = None
    is_active: Optional[bool] = None
    show_branding: Optional[bool] = None
    allowed_domains: Optional[List[str]] = None

class WidgetChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class WidgetChatResponse(BaseModel):
    response: str
    session_id: str
    confidence: float
    sources: List[dict] = []

class WidgetConfigResponse(BaseModel):
    widget_key: str
    primary_color: str
    widget_position: str
    welcome_message: str
    placeholder_text: str
    widget_title: str
    show_branding: bool
    is_active: bool
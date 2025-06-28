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
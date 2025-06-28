# models.py - Database models and setup
import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

# Database setup - SQLite compatible
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./saas_chatbot.db")

# Handle SQLite vs PostgreSQL
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models - SQLite compatible
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    # Relationship
    knowledge_bases = relationship("KnowledgeBase", back_populates="owner")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    website_url = Column(String)
    status = Column(String, default="not_ready")  # not_ready, processing, ready, error
    total_chunks = Column(Integer, default=0)
    last_updated = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    # Relationship
    owner = relationship("User", back_populates="knowledge_bases")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

# Initialize database
def init_database():
    """Initialize database with tables"""
    create_tables()
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    init_database()
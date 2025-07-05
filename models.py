# models.py - Fixed Database models and setup for PostgreSQL
import os
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship
from sqlalchemy.sql import func
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

# Helper function for UTC datetime
def utc_now():
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)

def get_database_url():
    """Construct database URL from environment variables"""
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    # Fallback to full DATABASE_URL if components not available
    if all([db_host, db_name, db_user, db_password]):
        return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    else:
        return os.getenv("DATABASE_URL", "sqlite:///./saas_chatbot.db")

DATABASE_URL = get_database_url()

# Create engine with PostgreSQL optimizations
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # Enables pessimistic disconnect handling
        pool_recycle=300,    # Recycle connections after 5 minutes
        echo=False           # Set to True for SQL logging during development
    )
    logger.info(f"✅ Connected to PostgreSQL database")
else:
    # Fallback to SQLite for development
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    logger.info(f"✅ Connected to SQLite database")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models - PostgreSQL optimized with fixed datetime handling
class User(Base):
    __tablename__ = "users"
    
    # Use UUID for better performance and uniqueness
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    # Fixed: Use func.now() for database-level timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    # Relationships
    knowledge_bases = relationship("KnowledgeBase", back_populates="owner", cascade="all, delete-orphan")
    chat_widgets = relationship("ChatWidget", back_populates="owner", cascade="all, delete-orphan")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    website_url = Column(String(500))
    status = Column(String(50), default="not_ready", nullable=False)  # not_ready, processing, ready, error
    total_chunks = Column(Integer, default=0, nullable=False)
    last_updated = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    # Relationships
    owner = relationship("User", back_populates="knowledge_bases")
    widgets = relationship("ChatWidget", back_populates="knowledge_base", cascade="all, delete-orphan")

class ChatWidget(Base):
    __tablename__ = "chat_widgets"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    knowledge_base_id = Column(String, ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False, index=True)
    widget_key = Column(String(255), unique=True, index=True, nullable=False)  # Public API key for widget
    
    # Widget Configuration
    name = Column(String(255), nullable=False)
    website_url = Column(String(500))  # Where the widget will be embedded
    
    # Appearance Settings
    primary_color = Column(String(20), default="#2563eb")
    widget_position = Column(String(50), default="bottom-right")
    welcome_message = Column(String(500), default="Hi! How can I help you today?")
    placeholder_text = Column(String(255), default="Type your message...")
    widget_title = Column(String(255), default="Chat Support")
    
    # Behavior Settings
    is_active = Column(Boolean, default=True, nullable=False)
    show_branding = Column(Boolean, default=True, nullable=False)
    allowed_domains = Column(Text)  # JSON array of allowed domains
    
    # Analytics
    total_conversations = Column(Integer, default=0, nullable=False)
    total_messages = Column(Integer, default=0, nullable=False)
    last_used = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        if 'widget_key' not in kwargs:
            kwargs['widget_key'] = 'widget_' + str(uuid.uuid4()).replace('-', '')[:16]
        super().__init__(**kwargs)
    
    # Relationships
    owner = relationship("User", back_populates="chat_widgets")
    knowledge_base = relationship("KnowledgeBase", back_populates="widgets")
    conversations = relationship("WidgetConversation", back_populates="widget", cascade="all, delete-orphan")

class WidgetConversation(Base):
    __tablename__ = "widget_conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    widget_id = Column(String, ForeignKey("chat_widgets.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)  # Browser session ID
    
    # Message details
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    confidence_score = Column(Float)
    response_time_ms = Column(Integer)
    
    # Metadata
    user_ip = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    referrer_url = Column(String(500))
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False, index=True)
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    # Relationship
    widget = relationship("ChatWidget", back_populates="conversations")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test database connection
def test_database_connection():
    """Test the database connection"""
    try:
        db = SessionLocal()
        # Simple query to test connection
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

# Create tables
def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise

# Initialize database
def init_database():
    """Initialize database with tables"""
    logger.info("🔄 Initializing database...")
    
    # Test connection first
    if not test_database_connection():
        raise Exception("Cannot connect to database")
    
    # Create tables
    create_tables()
    
    logger.info("✅ Database initialized successfully")

if __name__ == "__main__":
    init_database()
# models.py - Database models and setup
import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Boolean, ForeignKey, Float
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

class ChatWidget(Base):
    __tablename__ = "chat_widgets"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    knowledge_base_id = Column(String, ForeignKey("knowledge_bases.id"), nullable=False)
    widget_key = Column(String, unique=True, index=True, nullable=False)  # Public API key for widget
    
    # Widget Configuration
    name = Column(String, nullable=False)
    website_url = Column(String)  # Where the widget will be embedded
    
    # Appearance Settings
    primary_color = Column(String, default="#2563eb")  # Blue
    widget_position = Column(String, default="bottom-right")  # bottom-right, bottom-left, etc.
    welcome_message = Column(String, default="Hi! How can I help you today?")
    placeholder_text = Column(String, default="Type your message...")
    widget_title = Column(String, default="Chat Support")
    
    # Behavior Settings
    is_active = Column(Boolean, default=True)
    show_branding = Column(Boolean, default=True)  # Show "Powered by YourApp"
    allowed_domains = Column(Text)  # JSON array of allowed domains
    
    # Analytics
    total_conversations = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    last_used = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        if 'widget_key' not in kwargs:
            kwargs['widget_key'] = 'widget_' + str(uuid.uuid4()).replace('-', '')[:16]
        super().__init__(**kwargs)
    
    # Relationships
    owner = relationship("User", backref="chat_widgets")
    knowledge_base = relationship("KnowledgeBase", backref="widgets")

class WidgetConversation(Base):
    __tablename__ = "widget_conversations"
    
    id = Column(String, primary_key=True)
    widget_id = Column(String, ForeignKey("chat_widgets.id"), nullable=False)
    session_id = Column(String, nullable=False)  # Browser session ID
    
    # Message details
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    confidence_score = Column(Float)
    response_time_ms = Column(Integer)
    
    # Metadata
    user_ip = Column(String)
    user_agent = Column(String)
    referrer_url = Column(String)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    # Relationship
    widget = relationship("ChatWidget", backref="conversations")

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
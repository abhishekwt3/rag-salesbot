# models.py - Consolidated database models for PostgreSQL with subscription support
import os
import uuid
import enum
from datetime import datetime, timezone, timedelta
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text, Boolean, ForeignKey, Float, Enum
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

# Subscription Enums
class SubscriptionPlan(enum.Enum):
    BASIC = "basic"
    PRO = "pro" 
    ENTERPRISE = "enterprise"

class SubscriptionStatus(enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    TRIALING = "trialing"
    EXPIRED = "expired"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

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
    subscription = relationship("Subscription", back_populates="user", uselist=False)

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

# Subscription Models
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Plan details
    plan = Column(Enum(SubscriptionPlan), nullable=False, default=SubscriptionPlan.BASIC)
    status = Column(Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.TRIALING)
    
    # Razorpay details
    razorpay_subscription_id = Column(String(255), unique=True, index=True)
    razorpay_plan_id = Column(String(255))
    razorpay_customer_id = Column(String(255))
    
    # Pricing
    amount = Column(Integer, nullable=False)  # Amount in smallest currency unit (e.g., paise for INR)
    currency = Column(String(10), nullable=False, default="INR")
    billing_cycle = Column(String(20), nullable=False, default="monthly")  # monthly, yearly
    
    # Plan limits
    max_knowledge_bases = Column(Integer, nullable=False)
    max_total_chunks = Column(Integer, nullable=False)  # Total chunks across all KBs
    
    # Trial and billing dates
    trial_start = Column(DateTime(timezone=True))
    trial_end = Column(DateTime(timezone=True))
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    
    # Usage tracking
    current_chunk_usage = Column(Integer, default=0, nullable=False)
    current_kb_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    canceled_at = Column(DateTime(timezone=True))
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription", cascade="all, delete-orphan")
    
    @classmethod
    def get_plan_details(cls, plan: SubscriptionPlan):
        """Get plan pricing and limits"""
        plan_configs = {
            SubscriptionPlan.BASIC: {
                "name": "Basic",
                "amount_usd": 500,  # $5.00 in cents
                "amount_inr": 42000,  # ₹420 in paise (approx $5)
                "max_knowledge_bases": 5,
                "max_total_chunks": 200,
                "description": "Perfect for small businesses"
            },
            SubscriptionPlan.PRO: {
                "name": "Pro", 
                "amount_usd": 2500,  # $25.00 in cents
                "amount_inr": 210000,  # ₹2100 in paise (approx $25)
                "max_knowledge_bases": 30,
                "max_total_chunks": 1500,
                "description": "For growing businesses"
            },
            SubscriptionPlan.ENTERPRISE: {
                "name": "Enterprise",
                "amount_usd": 20000,  # $200.00 in cents
                "amount_inr": 1680000,  # ₹16800 in paise (approx $200)
                "max_knowledge_bases": -1,  # Unlimited
                "max_total_chunks": -1,  # Unlimited
                "description": "For large organizations"
            }
        }
        return plan_configs.get(plan)
    
    def can_create_knowledge_base(self):
        """Check if user can create a new knowledge base"""
        if self.max_knowledge_bases == -1:  # Unlimited
            return True
        return self.current_kb_count < self.max_knowledge_bases
    
    def can_add_chunks(self, chunk_count: int):
        """Check if user can add more chunks"""
        if self.max_total_chunks == -1:  # Unlimited
            return True
        return (self.current_chunk_usage + chunk_count) <= self.max_total_chunks
    
    def get_remaining_chunks(self):
        """Get remaining chunk allowance"""
        if self.max_total_chunks == -1:
            return -1  # Unlimited
        return max(0, self.max_total_chunks - self.current_chunk_usage)
    
    def is_trial_active(self):
        """Check if trial is still active"""
        if not self.trial_end:
            return False
        return datetime.now(timezone.utc) < self.trial_end
    
    def is_subscription_active(self):
        """Check if subscription is active (including trial)"""
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Razorpay payment details
    razorpay_payment_id = Column(String(255), unique=True, index=True)
    razorpay_order_id = Column(String(255))
    razorpay_signature = Column(Text)
    
    # Payment details
    amount = Column(Integer, nullable=False)  # Amount in smallest currency unit
    currency = Column(String(10), nullable=False, default="INR")
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Metadata
    payment_method = Column(String(50))  # card, upi, netbanking, etc.
    failure_reason = Column(Text)
    receipt_url = Column(String(500))
    
    # Billing period this payment covers
    billing_period_start = Column(DateTime(timezone=True))
    billing_period_end = Column(DateTime(timezone=True))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    paid_at = Column(DateTime(timezone=True))
    
    def __init__(self, **kwargs):
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid.uuid4())
        super().__init__(**kwargs)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="payments")
    user = relationship("User")

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
    logger.info("📄 Initializing database...")
    
    # Test connection first
    if not test_database_connection():
        raise Exception("Cannot connect to database")
    
    # Create tables
    create_tables()
    
    logger.info("✅ Database initialized successfully")

if __name__ == "__main__":
    init_database()
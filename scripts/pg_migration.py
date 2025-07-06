# migrate_to_postgresql.py
import os
import sys
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from models import Base, engine, SessionLocal, test_database_connection, init_database
from sqlalchemy import inspect, text

def check_postgresql_connection():
    """Verify PostgreSQL connection"""
    logger.info("🔍 Testing PostgreSQL connection...")
    
    try:
        # Test basic connection
        if not test_database_connection():
            raise Exception("Basic connection test failed")
        
        # Test PostgreSQL specific features
        db = SessionLocal()
        result = db.execute(text("SELECT version()"))
        version = result.scalar()
        logger.info(f"✅ Connected to: {version}")
        db.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        return False

def create_database_schema():
    """Create all tables in PostgreSQL"""
    logger.info("🔄 Creating database schema...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"✅ Created tables: {tables}")
        
        # Verify specific tables
        required_tables = ['users', 'knowledge_bases', 'chat_widgets', 'widget_conversations']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            logger.error(f"❌ Missing tables: {missing_tables}")
            return False
        
        logger.info("✅ All required tables created successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create schema: {e}")
        return False

def verify_database_setup():
    """Verify the database is set up correctly"""
    logger.info("🔍 Verifying database setup...")
    
    try:
        db = SessionLocal()
        
        # Test each table with a simple query
        tables_to_test = [
            ("users", "SELECT COUNT(*) FROM users"),
            ("knowledge_bases", "SELECT COUNT(*) FROM knowledge_bases"),
            ("chat_widgets", "SELECT COUNT(*) FROM chat_widgets"),
            ("widget_conversations", "SELECT COUNT(*) FROM widget_conversations")
        ]
        
        for table_name, query in tables_to_test:
            try:
                result = db.execute(text(query))
                count = result.scalar()
                logger.info(f"✅ {table_name}: {count} records")
            except Exception as e:
                logger.error(f"❌ {table_name}: {e}")
                return False
        
        db.close()
        logger.info("✅ Database verification completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main migration process"""
    logger.info("🚀 Starting PostgreSQL migration...")
    
    # Step 1: Check connection
    if not check_postgresql_connection():
        logger.error("❌ Cannot connect to PostgreSQL. Check your credentials.")
        return False
    
    # Step 2: Create schema
    if not create_database_schema():
        logger.error("❌ Failed to create database schema.")
        return False
    
    # Step 3: Verify setup
    if not verify_database_setup():
        logger.error("❌ Database verification failed.")
        return False
    
    logger.info("🎉 PostgreSQL migration completed successfully!")
    logger.info("🔧 Your application is now ready to use PostgreSQL")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
# migrate_database.py - Update database with widget tables
import os
import sys
from datetime import datetime

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import Base, engine, User, KnowledgeBase, ChatWidget, WidgetConversation
from sqlalchemy import inspect

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate_database():
    """Migrate database to include widget tables"""
    print("🔄 Starting database migration...")
    
    # Get current tables
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"📊 Existing tables: {existing_tables}")
    
    # Check what needs to be created
    required_tables = ['users', 'knowledge_bases', 'chat_widgets', 'widget_conversations']
    missing_tables = [table for table in required_tables if table not in existing_tables]
    
    if missing_tables:
        print(f"➕ Creating missing tables: {missing_tables}")
        
        # Create all tables (will only create missing ones)
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database migration completed!")
        
        # Verify tables were created
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        print(f"📊 Tables after migration: {new_tables}")
        
        # Check widget-specific tables
        if 'chat_widgets' in new_tables:
            print("✅ chat_widgets table created")
        if 'widget_conversations' in new_tables:
            print("✅ widget_conversations table created")
            
    else:
        print("✅ All required tables already exist")
    
    print("🎉 Migration complete!")

if __name__ == "__main__":
    migrate_database()
# test_fixed_models.py
import os
from dotenv import load_dotenv
load_dotenv()

def test_models():
    try:
        print("🔍 Testing fixed models.py...")
        
        # Import the models
        from models import init_database, SessionLocal, User, KnowledgeBase
        from sqlalchemy import text
        
        # Test database initialization
        print("🔄 Initializing database...")
        init_database()
        print("✅ Database initialized successfully")
        
        # Test creating a user
        print("👤 Testing user creation...")
        db = SessionLocal()
        
        test_user = User(
            email="test@example.com",
            hashed_password="test_hash_123",
            full_name="Test User"
        )
        
        db.add(test_user)
        db.commit()
        print("✅ User created successfully")
        
        # Test querying
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        print(f"✅ Users in database: {user_count}")
        
        # Test creating knowledge base
        print("📚 Testing knowledge base creation...")
        test_kb = KnowledgeBase(
            user_id=test_user.id,
            name="Test Knowledge Base",
            description="Test description"
        )
        
        db.add(test_kb)
        db.commit()
        print("✅ Knowledge base created successfully")
        
        # Clean up
        db.delete(test_kb)
        db.delete(test_user)
        db.commit()
        db.close()
        
        print("🎉 All tests passed! PostgreSQL is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_models()
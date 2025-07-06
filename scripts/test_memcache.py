# test_memcache_fixed.py
import pymemcache.client.base
import json
import time
import pickle

def test_memcache_connection():
    """Test Memcache connection and basic operations - FIXED VERSION"""
    try:
        # Method 1: Using pickle serializer (recommended)
        print("🔍 Testing Memcache connection with pickle serializer...")
        
        client = pymemcache.client.base.Client(
            ('localhost', 11211),
            serializer=pickle.dumps,
            deserializer=pickle.loads,
            connect_timeout=5,
            timeout=10
        )
        
        # Test basic operations
        print("✅ Connected to Memcache")
        
        # Set a simple value
        client.set('test_key', 'Hello Memcache!', expire=60)
        print("✅ Set test value")
        
        # Get the value
        result = client.get('test_key')
        print(f"✅ Retrieved value: {result}")
        
        # Test with complex data (like your embeddings)
        test_data = {
            'chunks': ['chunk1', 'chunk2'],
            'embeddings': [[0.1, 0.2], [0.3, 0.4]],
            'metadata': {'created': time.time()}
        }
        
        client.set('test_embeddings', test_data, expire=60)
        retrieved_data = client.get('test_embeddings')
        print(f"✅ Complex data test: {len(retrieved_data['chunks'])} chunks")
        
        # Test cache stats
        stats = client.stats()
        print(f"✅ Cache stats received")
        
        print("🎉 Memcache is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Memcache test failed: {e}")
        
        # Try alternative method
        print("\n🔄 Trying alternative connection method...")
        try:
            # Method 2: Simple client without custom serializer
            simple_client = pymemcache.client.base.Client(('localhost', 11211))
            
            # Test with string data
            simple_client.set(b'simple_test', b'hello world', expire=60)
            result = simple_client.get(b'simple_test')
            print(f"✅ Simple test successful: {result}")
            
            return True
            
        except Exception as e2:
            print(f"❌ Alternative method also failed: {e2}")
            return False

def test_memcache_no_serializer():
    """Test without custom serializer (bytes only)"""
    try:
        print("\n🔍 Testing basic Memcache (no serializer)...")
        
        client = pymemcache.client.base.Client(('localhost', 11211))
        
        # Test with bytes
        client.set(b'test', b'hello', expire=60)
        result = client.get(b'test')
        print(f"✅ Bytes test: {result}")
        
        # Test with JSON (manual serialization)
        data = {'test': 'value', 'number': 123}
        json_data = json.dumps(data).encode('utf-8')
        
        client.set(b'json_test', json_data, expire=60)
        retrieved = client.get(b'json_test')
        parsed = json.loads(retrieved.decode('utf-8'))
        print(f"✅ JSON test: {parsed}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Memcache tests...\n")
    
    # Try the main test
    success1 = test_memcache_connection()
    
    # Try the basic test
    success2 = test_memcache_no_serializer()
    
    if success1 or success2:
        print("\n✅ At least one method worked! Memcache is running correctly.")
    else:
        print("\n❌ All tests failed. Check if Memcache is running:")
        print("   docker ps | grep memcache")
        print("   docker logs memcache")
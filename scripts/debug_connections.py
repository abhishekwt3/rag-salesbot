# debug_connections.py
import os
import pymemcache.client.base
import pickle

def test_memcache():
    print("🔍 Testing Memcache connection...")
    
    # Debug environment variables
    host = os.getenv('MEMCACHE_HOST', 'localhost')
    port = os.getenv('MEMCACHE_PORT', '11211')
    print(f"Host: {host}, Port: {port} (type: {type(port)})")
    
    # Convert port to int
    port_int = int(port)
    print(f"Port as int: {port_int} (type: {type(port_int)})")
    
    try:
        client = pymemcache.client.base.Client(
            (host, port_int),
            serializer=pickle.dumps,
            deserializer=pickle.loads,
            connect_timeout=5,
            timeout=10
        )
        
        # Test basic operation
        client.set('debug_test', 'success', expire=60)
        result = client.get('debug_test')
        print(f"✅ Memcache test successful: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Memcache test failed: {e}")
        return False

def test_environment():
    print("🔍 Environment variables:")
    env_vars = ['MEMCACHE_HOST', 'MEMCACHE_PORT', 'AWS_ACCESS_KEY_ID', 'S3_EMBEDDINGS_BUCKET']
    for var in env_vars:
        value = os.getenv(var, 'NOT_SET')
        print(f"  {var}: {value}")

if __name__ == "__main__":
    test_environment()
    print()
    test_memcache()
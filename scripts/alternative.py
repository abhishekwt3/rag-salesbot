# alternative_memcache_setup.py
import os
import pymemcache.client.base

def test_alternative_setup():
    """Try different client initialization approaches"""
    
    print("🔍 Method 1: Using default serde...")
    try:
        from pymemcache.client.base import Client
        client = Client(('localhost', 11211))
        # Use manual JSON serialization
        import json
        data = json.dumps({'test': 'data'}).encode('utf-8')
        client.set(b'test_json', data)
        result = client.get(b'test_json')
        parsed = json.loads(result.decode('utf-8'))
        print(f"✅ JSON serialization works: {parsed}")
        return client
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    print("\n🔍 Method 2: Using PooledClient...")
    try:
        from pymemcache.client.base import PooledClient
        client = PooledClient(('localhost', 11211))
        client.set(b'test_pooled', b'pooled_data')
        result = client.get(b'test_pooled')
        print(f"✅ PooledClient works: {result}")
        return client
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    print("\n🔍 Method 3: HashClient...")
    try:
        from pymemcache.client.hash import HashClient
        client = HashClient([('localhost', 11211)])
        client.set(b'test_hash', b'hash_data')
        result = client.get(b'test_hash')
        print(f"✅ HashClient works: {result}")
        return client
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    return None

if __name__ == "__main__":
    test_alternative_setup()
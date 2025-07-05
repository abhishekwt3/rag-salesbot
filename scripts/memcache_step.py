# debug_memcache_step_by_step.py
import os
import pymemcache.client.base
import pickle

def test_minimal_client():
    """Test with absolute minimal parameters"""
    print("🔍 Step 1: Testing minimal client...")
    try:
        client = pymemcache.client.base.Client(('localhost', 11211))
        client.set(b'test', b'minimal')
        result = client.get(b'test')
        print(f"✅ Minimal client works: {result}")
        return True
    except Exception as e:
        print(f"❌ Minimal client failed: {e}")
        return False

def test_with_serializer():
    """Test adding serializer"""
    print("\n🔍 Step 2: Testing with serializer...")
    try:
        client = pymemcache.client.base.Client(
            ('localhost', 11211),
            serializer=pickle.dumps,
            deserializer=pickle.loads
        )
        client.set('test', 'with_serializer')
        result = client.get('test')
        print(f"✅ Serializer works: {result}")
        return True
    except Exception as e:
        print(f"❌ Serializer failed: {e}")
        return False

def test_with_timeouts():
    """Test adding timeout parameters one by one"""
    print("\n🔍 Step 3: Testing with connect_timeout...")
    try:
        client = pymemcache.client.base.Client(
            ('localhost', 11211),
            serializer=pickle.dumps,
            deserializer=pickle.loads,
            connect_timeout=5
        )
        client.set('test', 'with_connect_timeout')
        result = client.get('test')
        print(f"✅ connect_timeout works: {result}")
    except Exception as e:
        print(f"❌ connect_timeout failed: {e}")
        return False

    print("\n🔍 Step 4: Testing with both timeouts...")
    try:
        client = pymemcache.client.base.Client(
            ('localhost', 11211),
            serializer=pickle.dumps,
            deserializer=pickle.loads,
            connect_timeout=5,
            timeout=10
        )
        client.set('test', 'with_both_timeouts')
        result = client.get('test')
        print(f"✅ Both timeouts work: {result}")
        return True
    except Exception as e:
        print(f"❌ Both timeouts failed: {e}")
        return False

def test_env_variables():
    """Test with environment variables"""
    print("\n🔍 Step 5: Testing with env variables...")
    
    # Set environment variables
    os.environ['MEMCACHE_HOST'] = 'localhost'
    os.environ['MEMCACHE_PORT'] = '11211'
    
    try:
        # Get from env (same as your code)
        memcache_host = os.getenv('MEMCACHE_HOST', 'localhost')
        memcache_port = int(os.getenv('MEMCACHE_PORT', '11211'))
        
        print(f"Host: {memcache_host}, Port: {memcache_port} (type: {type(memcache_port)})")
        
        client = pymemcache.client.base.Client(
            (memcache_host, memcache_port),
            serializer=pickle.dumps,
            deserializer=pickle.loads,
            connect_timeout=5,
            timeout=10
        )
        client.set('test', 'env_variables')
        result = client.get('test')
        print(f"✅ Env variables work: {result}")
        return True
    except Exception as e:
        print(f"❌ Env variables failed: {e}")
        return False

def test_with_expire():
    """Test with expire parameter"""
    print("\n🔍 Step 6: Testing with expire parameter...")
    try:
        client = pymemcache.client.base.Client(
            ('localhost', 11211),
            serializer=pickle.dumps,
            deserializer=pickle.loads,
            connect_timeout=5,
            timeout=10
        )
        # This might be the issue - expire parameter
        client.set('test', 'with_expire', expire=1)
        result = client.get('test')
        print(f"✅ Expire parameter works: {result}")
        return True
    except Exception as e:
        print(f"❌ Expire parameter failed: {e}")
        return False

def check_pymemcache_version():
    """Check pymemcache version"""
    print("\n🔍 Checking pymemcache version...")
    try:
        import pymemcache
        print(f"pymemcache version: {pymemcache.__version__}")
    except:
        print("Could not determine pymemcache version")

if __name__ == "__main__":
    print("🚀 Deep debugging memcache client issue...\n")
    
    check_pymemcache_version()
    
    # Run tests step by step
    tests = [
        test_minimal_client,
        test_with_serializer, 
        test_with_timeouts,
        test_env_variables,
        test_with_expire
    ]
    
    for test in tests:
        success = test()
        if not success:
            print(f"\n❌ Found the issue at: {test.__name__}")
            break
        print("✅ This step passed")
    
    print("\n🏁 Debug complete!")
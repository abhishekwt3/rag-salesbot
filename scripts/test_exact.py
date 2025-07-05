# test_exact_setup.py
import os
os.environ['MEMCACHE_HOST'] = 'localhost'
os.environ['MEMCACHE_PORT'] = '11211'

# Test the exact import and setup from your saas_embeddings.py
import pymemcache.client.base
import pickle

try:
    memcache_host = os.getenv('MEMCACHE_HOST', 'localhost')
    memcache_port = int(os.getenv('MEMCACHE_PORT', '11211'))
    
    client = pymemcache.client.base.Client(
        (memcache_host, memcache_port),
        serde=pymemcache.serde.pickle_serde,  # Use serde instead
        connect_timeout=5,
        timeout=10
    )
    
    client.set('test', 'connection', expire=1)
    print("✅ Memcache setup works!")
    
except Exception as e:
    print(f"❌ Error: {e}")
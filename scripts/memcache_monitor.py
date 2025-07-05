# quick_monitor.py
import pymemcache.client.base
import pymemcache.serde

def check_memcache_usage():
    try:
        client = pymemcache.client.base.Client(
            ('localhost', 11211),
            serde=pymemcache.serde.pickle_serde
        )
        
        stats = client.stats()
        print("📊 Memcache Statistics:")
        print(f"  Total items: {stats.get(b'curr_items', 0)}")
        print(f"  Cache hits: {stats.get(b'get_hits', 0)}")
        print(f"  Cache misses: {stats.get(b'get_misses', 0)}")
        
        hits = int(stats.get(b'get_hits', 0))
        misses = int(stats.get(b'get_misses', 0))
        total = hits + misses
        
        if total > 0:
            hit_rate = (hits / total) * 100
            print(f"  Hit rate: {hit_rate:.1f}%")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_memcache_usage()
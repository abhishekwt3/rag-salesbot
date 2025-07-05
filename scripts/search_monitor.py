# search_monitor.py - Monitor search performance in production
import time
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
from typing import Dict, List

from saas_embeddings import SaaSVectorStore

class SearchPerformanceMonitor:
    """Monitor and analyze search performance in production"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.search_times = deque(maxlen=window_size)
        self.stats = defaultdict(list)
        self.logger = logging.getLogger(__name__)
    
    def record_search(self, query: str, num_results: int, search_time: float, 
                     index_type: str = "unknown", dataset_size: int = 0):
        """Record a search operation"""
        
        search_data = {
            'timestamp': datetime.now().isoformat(),
            'query_length': len(query),
            'num_results': num_results,
            'search_time_ms': search_time * 1000,
            'index_type': index_type,
            'dataset_size': dataset_size
        }
        
        self.search_times.append(search_data)
        
        # Log slow searches
        if search_time > 0.01:  # > 10ms
            self.logger.warning(f"Slow search: {search_time*1000:.1f}ms for query '{query[:50]}...'")
    
    def get_performance_stats(self) -> dict:
        """Get current performance statistics"""
        if not self.search_times:
            return {"error": "No search data available"}
        
        times_ms = [s['search_time_ms'] for s in self.search_times]
        
        stats = {
            'total_searches': len(self.search_times),
            'avg_time_ms': sum(times_ms) / len(times_ms),
            'min_time_ms': min(times_ms),
            'max_time_ms': max(times_ms),
            'p50_time_ms': sorted(times_ms)[len(times_ms)//2],
            'p95_time_ms': sorted(times_ms)[int(len(times_ms)*0.95)],
            'p99_time_ms': sorted(times_ms)[int(len(times_ms)*0.99)],
            'slow_searches': len([t for t in times_ms if t > 10]),
            'time_window': f"Last {len(self.search_times)} searches"
        }
        
        # Add recommendations
        stats['recommendations'] = self._generate_recommendations(stats)
        
        return stats
    
    def _generate_recommendations(self, stats: dict) -> list:
        """Generate performance recommendations"""
        recommendations = []
        
        if stats['p95_time_ms'] > 10:
            recommendations.append("Consider optimizing index - 95th percentile > 10ms")
        
        if stats['slow_searches'] > len(self.search_times) * 0.05:
            recommendations.append("High percentage of slow searches - investigate index configuration")
        
        if stats['avg_time_ms'] < 1:
            recommendations.append("Excellent performance - current configuration is optimal")
        
        return recommendations
    
    def print_performance_report(self):
        """Print a performance report"""
        stats = self.get_performance_stats()
        
        print("\n📊 Search Performance Report")
        print("=" * 40)
        print(f"Total searches: {stats['total_searches']:,}")
        print(f"Average time: {stats['avg_time_ms']:.2f}ms")
        print(f"P50 (median): {stats['p50_time_ms']:.2f}ms")
        print(f"P95: {stats['p95_time_ms']:.2f}ms")
        print(f"P99: {stats['p99_time_ms']:.2f}ms")
        print(f"Slow searches (>10ms): {stats['slow_searches']}")
        
        print(f"\n💡 Recommendations:")
        for rec in stats['recommendations']:
            print(f"   • {rec}")

# Integration with your vector store
class MonitoredSaaSVectorStore(SaaSVectorStore):
    """SaaSVectorStore with performance monitoring"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.monitor = SearchPerformanceMonitor()
    
    async def search_similar(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search with performance monitoring"""
        start_time = time.time()
        
        # Perform search
        results = await super().search_similar(query, max_results)
        
        # Record performance
        search_time = time.time() - start_time
        index_type = type(self.index).__name__ if self.index else "none"
        
        self.monitor.record_search(
            query=query,
            num_results=len(results),
            search_time=search_time,
            index_type=index_type,
            dataset_size=len(self.chunks)
        )
        
        return results
    
    def get_performance_report(self) -> dict:
        """Get performance report"""
        return self.monitor.get_performance_stats()
    
    def print_performance_summary(self):
        """Print performance summary"""
        self.monitor.print_performance_report()

# Usage example:
"""
# Replace your vector store with monitored version
vector_store = MonitoredSaaSVectorStore(storage_dir="your_dir")

# Use normally
results = await vector_store.search_similar("test query", 10)

# Check performance periodically
vector_store.print_performance_summary()
"""
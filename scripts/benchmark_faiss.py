# benchmark_faiss.py - Compare FAISS index performance
import time
import numpy as np
import faiss
from typing import List, Dict
import matplotlib.pyplot as plt
import json
from pathlib import Path

class FAISSBenchmark:
    """Benchmark different FAISS index configurations"""
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.results = {}
    
    def generate_test_data(self, num_vectors: int, num_queries: int = 100):
        """Generate synthetic test data"""
        print(f"🔄 Generating {num_vectors:,} test vectors ({self.dimension}D)")
        
        # Generate random normalized vectors (simulating sentence embeddings)
        np.random.seed(42)  # For reproducible results
        
        vectors = np.random.random((num_vectors, self.dimension)).astype('float32')
        faiss.normalize_L2(vectors)
        
        queries = np.random.random((num_queries, self.dimension)).astype('float32')
        faiss.normalize_L2(queries)
        
        return vectors, queries
    
    def benchmark_flat_index(self, vectors: np.ndarray, queries: np.ndarray, k: int = 10):
        """Benchmark IndexFlatIP (exact search)"""
        print(f"\n📊 Benchmarking IndexFlatIP...")
        
        # Build index
        build_start = time.time()
        index = faiss.IndexFlatIP(self.dimension)
        index.add(vectors)
        build_time = time.time() - build_start
        
        # Search
        search_start = time.time()
        scores, indices = index.search(queries, k)
        search_time = time.time() - search_start
        
        avg_search_time = search_time / len(queries) * 1000  # ms per query
        
        print(f"   Build time: {build_time:.3f}s")
        print(f"   Search time: {search_time:.3f}s ({avg_search_time:.2f}ms per query)")
        print(f"   Memory usage: ~{vectors.nbytes / 1024**2:.1f} MB")
        
        return {
            'type': 'IndexFlatIP',
            'build_time': build_time,
            'search_time': search_time,
            'avg_search_time_ms': avg_search_time,
            'memory_mb': vectors.nbytes / 1024**2,
            'accuracy': 1.0  # Exact search
        }
    
    def benchmark_ivf_index(self, vectors: np.ndarray, queries: np.ndarray, k: int = 10, 
                          nlist: int = None, nprobe_values: List[int] = None):
        """Benchmark IndexIVFFlat with different nprobe values"""
        
        if nlist is None:
            nlist = min(int(4 * np.sqrt(len(vectors))), 65536)
        
        if nprobe_values is None:
            nprobe_values = [1, 5, 10, 20, 50, min(100, nlist)]
        
        print(f"\n🚀 Benchmarking IndexIVFFlat (nlist={nlist})...")
        
        results = []
        
        # Build index (done once)
        build_start = time.time()
        quantizer = faiss.IndexFlatIP(self.dimension)
        index = faiss.IndexIVFFlat(quantizer, self.dimension, nlist)
        
        # Train index
        train_vectors = vectors
        if len(vectors) > 100000:
            # Subsample for training
            indices = np.random.choice(len(vectors), 100000, replace=False)
            train_vectors = vectors[indices]
        
        index.train(train_vectors)
        index.add(vectors)
        build_time = time.time() - build_start
        
        print(f"   Build time: {build_time:.3f}s")
        
        # Test different nprobe values
        for nprobe in nprobe_values:
            if nprobe > nlist:
                continue
                
            index.nprobe = nprobe
            
            # Search
            search_start = time.time()
            scores, indices_result = index.search(queries, k)
            search_time = time.time() - search_start
            
            avg_search_time = search_time / len(queries) * 1000  # ms per query
            
            print(f"   nprobe={nprobe:3d}: {search_time:.3f}s ({avg_search_time:.2f}ms per query)")
            
            results.append({
                'type': f'IndexIVFFlat_nprobe_{nprobe}',
                'nprobe': nprobe,
                'build_time': build_time,
                'search_time': search_time,
                'avg_search_time_ms': avg_search_time,
                'memory_mb': vectors.nbytes / 1024**2,  # Approximate
            })
        
        return results
    
    def calculate_recall(self, true_results: np.ndarray, test_results: np.ndarray, k: int = 10):
        """Calculate recall@k between true and test results"""
        recall_sum = 0
        for i in range(len(true_results)):
            true_set = set(true_results[i][:k])
            test_set = set(test_results[i][:k])
            recall = len(true_set.intersection(test_set)) / len(true_set)
            recall_sum += recall
        
        return recall_sum / len(true_results)
    
    def run_comprehensive_benchmark(self, dataset_sizes: List[int] = None):
        """Run comprehensive benchmark across different dataset sizes"""
        
        if dataset_sizes is None:
            dataset_sizes = [100, 500, 1000, 5000, 10000, 50000]
        
        all_results = []
        
        for size in dataset_sizes:
            print(f"\n{'='*60}")
            print(f"🧪 Testing with {size:,} vectors")
            print(f"{'='*60}")
            
            vectors, queries = self.generate_test_data(size)
            
            # Benchmark Flat index
            flat_result = self.benchmark_flat_index(vectors, queries)
            flat_result['dataset_size'] = size
            all_results.append(flat_result)
            
            # Benchmark IVF index (only for larger datasets)
            if size >= 100:
                ivf_results = self.benchmark_ivf_index(vectors, queries)
                for result in ivf_results:
                    result['dataset_size'] = size
                    all_results.append(result)
        
        return all_results
    
    def save_results(self, results: List[Dict], filename: str = "faiss_benchmark_results.json"):
        """Save benchmark results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")
    
    def plot_results(self, results: List[Dict]):
        """Plot benchmark results"""
        try:
            import matplotlib.pyplot as plt
            
            # Group results by dataset size
            sizes = sorted(set(r['dataset_size'] for r in results))
            
            # Plot search time vs dataset size
            plt.figure(figsize=(12, 8))
            
            # Separate flat and IVF results
            flat_results = [r for r in results if r['type'] == 'IndexFlatIP']
            ivf_results = [r for r in results if 'IVFFlat' in r['type']]
            
            # Plot Flat index
            flat_sizes = [r['dataset_size'] for r in flat_results]
            flat_times = [r['avg_search_time_ms'] for r in flat_results]
            plt.plot(flat_sizes, flat_times, 'o-', label='IndexFlatIP (Exact)', linewidth=2, markersize=8)
            
            # Plot IVF with different nprobe values
            nprobe_values = sorted(set(r.get('nprobe', 0) for r in ivf_results if 'nprobe' in r))
            
            for nprobe in nprobe_values:
                ivf_subset = [r for r in ivf_results if r.get('nprobe') == nprobe]
                if ivf_subset:
                    sizes_subset = [r['dataset_size'] for r in ivf_subset]
                    times_subset = [r['avg_search_time_ms'] for r in ivf_subset]
                    plt.plot(sizes_subset, times_subset, 's--', label=f'IVFFlat nprobe={nprobe}', alpha=0.8)
            
            plt.xlabel('Dataset Size (number of vectors)')
            plt.ylabel('Average Search Time (ms per query)')
            plt.title('FAISS Index Performance Comparison')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.yscale('log')
            plt.xscale('log')
            
            plt.tight_layout()
            plt.savefig('faiss_benchmark.png', dpi=300, bbox_inches='tight')
            plt.show()
            
            print("📊 Plot saved as faiss_benchmark.png")
            
        except ImportError:
            print("⚠️ matplotlib not available, skipping plot generation")
    
    def generate_recommendations(self, results: List[Dict]):
        """Generate recommendations based on benchmark results"""
        print(f"\n🎯 Performance Recommendations:")
        print("="*50)
        
        # Group by dataset size
        size_groups = {}
        for result in results:
            size = result['dataset_size']
            if size not in size_groups:
                size_groups[size] = []
            size_groups[size].append(result)
        
        for size in sorted(size_groups.keys()):
            group = size_groups[size]
            print(f"\n📊 Dataset size: {size:,} vectors")
            
            # Find fastest option
            fastest = min(group, key=lambda x: x['avg_search_time_ms'])
            
            if size < 1000:
                print(f"   Recommendation: IndexFlatIP (exact search)")
                print(f"   Reason: Small dataset, exact search is fast enough")
            else:
                print(f"   Fastest option: {fastest['type']}")
                print(f"   Search time: {fastest['avg_search_time_ms']:.2f}ms per query")
                
                if 'nprobe' in fastest:
                    print(f"   Optimal nprobe: {fastest['nprobe']}")

def main():
    """Run the benchmark"""
    print("🚀 FAISS Performance Benchmark")
    print("="*50)
    
    benchmark = FAISSBenchmark()
    
    # Test with different dataset sizes
    results = benchmark.run_comprehensive_benchmark([
        100, 500, 1000, 2000, 5000, 10000, 20000, 50000
    ])
    
    # Save results
    benchmark.save_results(results)
    
    # Generate plot
    benchmark.plot_results(results)
    
    # Generate recommendations
    benchmark.generate_recommendations(results)
    
    print(f"\n✅ Benchmark complete!")

if __name__ == "__main__":
    main()
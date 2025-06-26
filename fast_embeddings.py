# fast_embeddings.py - Ultra Fast Sentence Transformers Implementation
import os
import json
import time
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import logging

# Fast sentence transformers
from sentence_transformers import SentenceTransformer
import faiss  # Ultra fast similarity search

logger = logging.getLogger(__name__)

class FastSentenceTransformerStore:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize with fastest sentence transformer model"""
        self.model_name = model_name
        self.model = None
        self.embeddings = None
        self.chunks = []
        self.index = None  # FAISS index for ultra-fast search
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
        self.ready = False
        self.last_updated = None
        
        # Speed optimizations
        self.batch_size = 32  # Process in batches for speed
        self.cache_file = "embeddings_cache.json"
        self.faiss_index_file = "faiss_index.bin"
        
    def _load_model(self):
        """Load sentence transformer model with optimizations"""
        if self.model is None:
            logger.info(f"Loading fast model: {self.model_name}")
            start_time = time.time()
            
            # Load with optimizations
            self.model = SentenceTransformer(self.model_name)
            
            # CPU optimizations
            self.model.eval()  # Set to evaluation mode
            
            load_time = time.time() - start_time
            logger.info(f"✅ Model loaded in {load_time:.2f}s")
    
    async def process_pages(self, pages: List[Dict]):
        """FAST processing with sentence transformers + FAISS"""
        logger.info(f"🚀 Fast Sentence Transformer processing for {len(pages)} pages...")
        total_start = time.time()
        
        # Load model
        self._load_model()
        
        # Step 1: Create chunks (same as before)
        logger.info("📝 Step 1: Creating chunks...")
        chunks_start = time.time()
        all_chunks = []
        
        for i, page in enumerate(pages):
            try:
                chunks = self._create_chunks(page)
                all_chunks.extend(chunks)
                if (i + 1) % 5 == 0:
                    logger.info(f"   📄 Processed {i+1}/{len(pages)} pages")
            except Exception as e:
                logger.error(f"   ❌ Error with page {i+1}: {e}")
                continue
        
        chunks_time = time.time() - chunks_start
        logger.info(f"✅ Created {len(all_chunks)} chunks in {chunks_time:.2f}s")
        
        if not all_chunks:
            logger.error("❌ No chunks created!")
            return
        
        # Step 2: Generate embeddings in FAST batches
        logger.info("🧠 Step 2: Generating sentence embeddings...")
        embeddings_start = time.time()
        
        # Extract texts for embedding
        texts = [chunk['text'] for chunk in all_chunks]
        
        # Generate embeddings in optimized batches
        embeddings = self._generate_embeddings_fast(texts)
        
        embeddings_time = time.time() - embeddings_start
        logger.info(f"✅ Generated {len(embeddings)} embeddings in {embeddings_time:.2f}s")
        logger.info(f"   ⚡ Speed: {len(embeddings)/embeddings_time:.0f} embeddings/second")
        
        # Step 3: Build FAISS index for ultra-fast search
        logger.info("🔍 Step 3: Building FAISS index...")
        faiss_start = time.time()
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Create FAISS index (ultra fast)
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (cosine with normalized vectors)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings_array)
        
        # Add to index
        self.index.add(embeddings_array)
        
        faiss_time = time.time() - faiss_start
        logger.info(f"✅ FAISS index built in {faiss_time:.2f}s")
        
        # Store data
        self.chunks = all_chunks
        self.embeddings = embeddings
        self.ready = True
        self.last_updated = datetime.now().isoformat()
        
        # Save to disk for fast loading
        self._save_to_disk()
        
        total_time = time.time() - total_start
        logger.info(f"🎉 COMPLETE! Total processing time: {total_time:.2f}s")
        logger.info(f"📊 Ready for ultra-fast semantic search: {len(self.chunks)} chunks")
    
    def _generate_embeddings_fast(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with speed optimizations"""
        logger.info(f"   🔄 Processing {len(texts)} texts in batches of {self.batch_size}")
        
        all_embeddings = []
        
        # Process in batches for speed
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            # Generate embeddings for batch
            batch_embeddings = self.model.encode(
                batch,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True  # For cosine similarity
            )
            
            all_embeddings.extend(batch_embeddings.tolist())
            
            if (i + self.batch_size) % 100 == 0:
                logger.info(f"   ⚡ Processed {min(i + self.batch_size, len(texts))}/{len(texts)} texts")
        
        return all_embeddings
    
    async def search_similar(self, query: str, max_results: int = 5) -> List[Dict]:
        """ULTRA FAST semantic search using FAISS"""
        if not self.ready:
            self._load_from_disk()
        
        if not self.ready or self.index is None:
            logger.error("❌ Search index not ready!")
            return []
        
        try:
            # Generate query embedding
            self._load_model()
            query_embedding = self.model.encode(
                [query], 
                normalize_embeddings=True,
                convert_to_numpy=True
            )
            
            # FAISS search (ultra fast!)
            search_start = time.time()
            scores, indices = self.index.search(query_embedding, max_results)
            search_time = time.time() - search_start
            
            logger.info(f"🔍 FAISS search completed in {search_time*1000:.1f}ms")
            
            # Format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunks):  # Valid index
                    results.append({
                        'text': self.chunks[idx]['text'],
                        'metadata': self.chunks[idx]['metadata'],
                        'score': float(score)  # Cosine similarity score
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _create_chunks(self, page: Dict) -> List[Dict]:
        """Create chunks from page content (same as before)"""
        try:
            content = page.get('content', '')
            if not content or len(content) < 100:
                return []
            
            # Sentence-based chunking for better semantic coherence
            sentences = [s.strip() for s in content.split('.') if s.strip()]
            
            chunks = []
            current_chunk = ""
            
            for sentence in sentences:
                # If adding this sentence would make chunk too long, save current chunk
                if len(current_chunk) + len(sentence) > 800:  # Optimal for sentence transformers
                    if current_chunk:
                        chunks.append({
                            'text': current_chunk.strip(),
                            'metadata': {
                                'source_url': page.get('url', ''),
                                'title': page.get('title', ''),
                                'chunk_index': len(chunks),
                                'scraped_at': page.get('scraped_at', '')
                            }
                        })
                    current_chunk = sentence
                else:
                    current_chunk += ". " + sentence
            
            # Add final chunk
            if current_chunk.strip():
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': {
                        'source_url': page.get('url', ''),
                        'title': page.get('title', ''),
                        'chunk_index': len(chunks),
                        'scraped_at': page.get('scraped_at', '')
                    }
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error creating chunks: {e}")
            return []
    
    def _save_to_disk(self):
        """Save embeddings and index to disk for fast loading"""
        try:
            # Save chunks and metadata
            data = {
                'chunks': self.chunks,
                'embeddings': self.embeddings,
                'last_updated': self.last_updated,
                'ready': self.ready,
                'model_name': self.model_name
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
            
            # Save FAISS index
            if self.index:
                faiss.write_index(self.index, self.faiss_index_file)
            
            logger.info(f"💾 Saved {len(self.chunks)} chunks and FAISS index to disk")
            
        except Exception as e:
            logger.error(f"Error saving to disk: {e}")
    
    def _load_from_disk(self):
        """Load embeddings and index from disk for instant startup"""
        try:
            # Load chunks and metadata
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                self.chunks = data.get('chunks', [])
                self.embeddings = data.get('embeddings', [])
                self.last_updated = data.get('last_updated')
                self.ready = data.get('ready', False)
            
            # Load FAISS index
            if os.path.exists(self.faiss_index_file):
                self.index = faiss.read_index(self.faiss_index_file)
            
            logger.info(f"📁 Loaded {len(self.chunks)} chunks and FAISS index from disk")
            
        except FileNotFoundError:
            logger.info("📁 No existing cache found")
        except Exception as e:
            logger.error(f"Error loading from disk: {e}")
    
    def is_ready(self) -> bool:
        if not self.ready:
            self._load_from_disk()
        return self.ready and len(self.chunks) > 0
    
    def get_total_chunks(self) -> int:
        return len(self.chunks)


# Updated requirements.txt additions:
"""
Add these to requirements.txt:

sentence-transformers==2.2.2
faiss-cpu==1.7.4
numpy==1.24.3
"""
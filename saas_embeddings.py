# saas_embeddings.py - Multi-tenant Vector Store with Memcache + GCS
import os
import json
import time
import numpy as np
import pickle
import gzip
from typing import List, Dict, Optional
from datetime import datetime
import logging
from pathlib import Path

# Fast sentence transformers
from sentence_transformers import SentenceTransformer
import faiss  # Ultra fast similarity search
import httpx

# Memcache and GCS clients
import pymemcache.client.base
import pymemcache.serde
import pickle
from google.cloud import storage
from google.api_core import exceptions as gcs_exceptions

logger = logging.getLogger(__name__)

class MemcacheGCSVectorStore:
    """Multi-tenant vector store using Memcache + GCS backend"""
    
    def __init__(self, user_id: str, knowledge_base_id: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize with user and knowledge base IDs"""
        self.user_id = user_id
        self.knowledge_base_id = knowledge_base_id
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
        
        # 🚀 Memcache + GCS Configuration
        self._setup_clients()
        
        # Cache keys for this knowledge base
        self.cache_prefix = f"embeddings:{user_id}:{knowledge_base_id}"
        self.chunks_key = f"{self.cache_prefix}:chunks"
        self.faiss_key = f"{self.cache_prefix}:faiss"
        self.metadata_key = f"{self.cache_prefix}:metadata"
        
        # GCS paths for this knowledge base
        self.gcs_prefix = f"embeddings/{user_id}/{knowledge_base_id}"
        self.gcs_chunks_key = f"{self.gcs_prefix}/chunks.json.gz"
        self.gcs_faiss_key = f"{self.gcs_prefix}/faiss_index.bin"
        self.gcs_metadata_key = f"{self.gcs_prefix}/metadata.json"
        
        # Google API key for LLM responses
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not found in environment")
        
        # Load existing data if available
        self._load_from_cache_or_gcs()
    
    def _setup_clients(self):
        """Setup Memcache and GCS clients"""
        try:
            # Memcache client
            memcache_host = os.getenv('MEMCACHE_HOST', 'localhost')
            memcache_port = int(os.getenv('MEMCACHE_PORT', '11211'))
            
            self.memcache = pymemcache.client.base.Client(
                (memcache_host, memcache_port),
                serde=pymemcache.serde.pickle_serde,  # Use serde instead
                connect_timeout=5,
                timeout=10
            )
            
            # Test memcache connection
            self.memcache.set('test', 'connection', expire=1)
            logger.info(f"✅ Connected to Memcache at {memcache_host}:{memcache_port}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Memcache: {e}")
            self.memcache = None
        
        try:
            # Google Cloud Storage client
            # Authentication will be handled by:
            # 1. GOOGLE_APPLICATION_CREDENTIALS environment variable (service account key file)
            # 2. Or default credentials if running on GCP
            self.gcs_client = storage.Client()
            
            self.gcs_bucket_name = os.getenv('GCS_EMBEDDINGS_BUCKET', 'your-embeddings-bucket')
            self.gcs_bucket = self.gcs_client.bucket(self.gcs_bucket_name)
            
            # Test GCS connection
            self.gcs_bucket.reload()
            logger.info(f"✅ Connected to GCS bucket: {self.gcs_bucket_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to GCS: {e}")
            self.gcs_client = None
    
    def _load_model(self):
        """Load sentence transformer model with optimizations"""
        if self.model is None:
            logger.info(f"Loading model: {self.model_name}")
            start_time = time.time()
            
            # Load with optimizations
            self.model = SentenceTransformer(self.model_name)
            self.model.eval()  # Set to evaluation mode
            
            load_time = time.time() - start_time
            logger.info(f"✅ Model loaded in {load_time:.2f}s")
    
    def _compress_data(self, data: bytes) -> bytes:
        """Compress data for storage efficiency"""
        return gzip.compress(data)
    
    def _decompress_data(self, compressed_data: bytes) -> bytes:
        """Decompress data"""
        return gzip.decompress(compressed_data)
    
    def _save_to_cache_and_gcs(self):
        """Save embeddings and index to Memcache + GCS"""
        try:
            save_start = time.time()
            
            # Prepare data for storage
            chunks_data = {
                'chunks': self.chunks,
                'embeddings': self.embeddings,
                'last_updated': self.last_updated,
                'ready': self.ready,
                'model_name': self.model_name
            }
            
            metadata = {
                'user_id': self.user_id,
                'knowledge_base_id': self.knowledge_base_id,
                'total_chunks': len(self.chunks),
                'last_updated': self.last_updated,
                'model_name': self.model_name,
                'ready': self.ready
            }
            
            # 🚀 Save to Memcache (fast, for immediate access)
            cache_success = self._save_to_memcache(chunks_data, metadata)
            
            # 💾 Save to GCS (persistent, for durability)
            gcs_success = self._save_to_gcs(chunks_data, metadata)
            
            save_time = time.time() - save_start
            
            if cache_success and gcs_success:
                logger.info(f"💾 Saved {len(self.chunks)} chunks to Memcache + GCS in {save_time:.2f}s")
            elif cache_success:
                logger.warning(f"⚠️ Saved to Memcache only (GCS failed) in {save_time:.2f}s")
            elif gcs_success:
                logger.warning(f"⚠️ Saved to GCS only (Memcache failed) in {save_time:.2f}s")
            else:
                logger.error(f"❌ Failed to save to both Memcache and GCS")
            
        except Exception as e:
            logger.error(f"Error saving to cache and GCS: {e}")
    
    def _save_to_memcache(self, chunks_data: dict, metadata: dict) -> bool:
        """Save data to Memcache"""
        if not self.memcache:
            return False
        
        try:
            # Cache with 1 hour TTL (3600 seconds)
            cache_ttl = int(os.getenv('MEMCACHE_TTL', '3600'))
            
            # Save chunks and embeddings (largest data)
            self.memcache.set(self.chunks_key, chunks_data, expire=cache_ttl)
            
            # Save FAISS index if available
            if self.index:
                faiss_data = faiss.serialize_index(self.index)
                faiss_bytes = faiss_data.tobytes() if hasattr(faiss_data, 'tobytes') else bytes(faiss_data)
                self.memcache.set(self.faiss_key, faiss_bytes, expire=cache_ttl)
    
            # Save metadata (small, longer TTL)
            self.memcache.set(self.metadata_key, metadata, expire=cache_ttl * 24)  # 24 hours
            
            logger.debug(f"✅ Cached data for {self.cache_prefix}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Memcache save error: {e}")
            return False
    
    def _save_to_gcs(self, chunks_data: dict, metadata: dict) -> bool:
        """Save data to Google Cloud Storage"""
        if not self.gcs_client:
            return False
        
        try:
            # Save compressed chunks data
            chunks_json = json.dumps(chunks_data).encode('utf-8')
            compressed_chunks = self._compress_data(chunks_json)
            
            chunks_blob = self.gcs_bucket.blob(self.gcs_chunks_key)
            chunks_blob.upload_from_string(
                compressed_chunks,
                content_type='application/gzip'
            )
            
            # Set custom metadata
            chunks_blob.metadata = {
                'user-id': self.user_id,
                'knowledge-base-id': self.knowledge_base_id,
                'total-chunks': str(len(self.chunks))
            }
            chunks_blob.patch()
            
            # Save FAISS index if available
            if self.index:
                faiss_data = faiss.serialize_index(self.index)
                faiss_bytes = faiss_data.tobytes() if hasattr(faiss_data, 'tobytes') else bytes(faiss_data)
                
                faiss_blob = self.gcs_bucket.blob(self.gcs_faiss_key)
                faiss_blob.upload_from_string(
                    faiss_bytes,
                    content_type='application/octet-stream'
                )
            
            # Save metadata
            metadata_blob = self.gcs_bucket.blob(self.gcs_metadata_key)
            metadata_blob.upload_from_string(
                json.dumps(metadata),
                content_type='application/json'
            )
            
            logger.debug(f"✅ Saved to GCS: {self.gcs_prefix}")
            return True
            
        except Exception as e:
            logger.error(f"❌ GCS save error: {e}")
            return False
    
    def _load_from_cache_or_gcs(self):
        """Load embeddings and index from Memcache or GCS"""
        try:
            load_start = time.time()
            # Try Memcache first (fast path)
            logger.info("🔍 Checking Memcache for existing data...")
            if self._load_from_memcache():
                load_time = time.time() - load_start
                logger.info(f"⚡ MEMCACHE HIT: Loaded {len(self.chunks)} chunks in {load_time:.3f}s (FAST PATH)")
                return
            logger.info("❌ Memcache miss - falling back to GCS...")
            
            # Fallback to GCS (slower but persistent)
            if self._load_from_gcs():
                gcs_load_time = time.time() - load_start
                logger.info(f"📁 GCS FALLBACK: Loaded {len(self.chunks)} chunks in {gcs_load_time:.3f}s (SLOW PATH)")
                # Cache in Memcache for next time
                self._cache_in_memcache()
                logger.info("💾 Cached GCS data to Memcache for faster future access")
                return
            
            logger.info(f"📁 No existing data found for {self.user_id}/{self.knowledge_base_id}")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def _load_from_memcache(self) -> bool:
        """Load data from Memcache"""
        if not self.memcache:
            return False
        
        try:
            # Load chunks and embeddings
            chunks_data = self.memcache.get(self.chunks_key)
            if not chunks_data:
                return False
            
            self.chunks = chunks_data.get('chunks', [])
            self.embeddings = chunks_data.get('embeddings', [])
            self.last_updated = chunks_data.get('last_updated')
            self.ready = chunks_data.get('ready', False)
            
            # Load FAISS index
            faiss_bytes = self.memcache.get(self.faiss_key)
            if faiss_bytes:
                faiss_data = np.frombuffer(faiss_bytes, dtype=np.uint8)
                self.index = faiss.deserialize_index(faiss_data)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Memcache load error: {e}")
            return False
    
    def _load_from_gcs(self) -> bool:
        """Load data from Google Cloud Storage"""
        if not self.gcs_client:
            return False
        
        try:
            # Load chunks data
            chunks_blob = self.gcs_bucket.blob(self.gcs_chunks_key)
            
            if not chunks_blob.exists():
                logger.debug(f"No GCS data found for {self.gcs_prefix}")
                return False
            
            compressed_data = chunks_blob.download_as_bytes()
            decompressed_data = self._decompress_data(compressed_data)
            chunks_data = json.loads(decompressed_data.decode('utf-8'))
            
            self.chunks = chunks_data.get('chunks', [])
            self.embeddings = chunks_data.get('embeddings', [])
            self.last_updated = chunks_data.get('last_updated')
            self.ready = chunks_data.get('ready', False)
            
            # Load FAISS index
            try:
                faiss_blob = self.gcs_bucket.blob(self.gcs_faiss_key)
                if faiss_blob.exists():
                    faiss_bytes = faiss_blob.download_as_bytes()
                    faiss_data = np.frombuffer(faiss_bytes, dtype=np.uint8)
                    self.index = faiss.deserialize_index(faiss_data)
                else:
                    logger.debug("No FAISS index found in GCS, will rebuild")
            except Exception as e:
                logger.debug(f"Error loading FAISS index from GCS: {e}")
            
            return True
            
        except gcs_exceptions.NotFound:
            logger.debug(f"No GCS data found for {self.gcs_prefix}")
            return False
        except Exception as e:
            logger.error(f"❌ GCS load error: {e}")
            return False
    
    def _cache_in_memcache(self):
        """Cache currently loaded data in Memcache"""
        if not self.memcache or not self.chunks:
            return
        
        chunks_data = {
            'chunks': self.chunks,
            'embeddings': self.embeddings,
            'last_updated': self.last_updated,
            'ready': self.ready,
            'model_name': self.model_name
        }
        
        metadata = {
            'user_id': self.user_id,
            'knowledge_base_id': self.knowledge_base_id,
            'total_chunks': len(self.chunks),
            'last_updated': self.last_updated,
            'ready': self.ready
        }
        
        self._save_to_memcache(chunks_data, metadata)
    
    def invalidate_cache(self):
        """Invalidate Memcache entries for this knowledge base"""
        if not self.memcache:
            return
        
        try:
            self.memcache.delete(self.chunks_key)
            self.memcache.delete(self.faiss_key) 
            self.memcache.delete(self.metadata_key)
            logger.info(f"🗑️ Invalidated cache for {self.cache_prefix}")
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
    
    # Keep all existing methods but replace storage calls
    async def process_pages(self, pages: List[Dict]):
        """Process pages into vector embeddings"""
        logger.info(f"🚀 Processing {len(pages)} pages for vector store...")
        total_start = time.time()
        
        # Load model
        self._load_model()
        
        # Step 1: Create chunks
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
        
        # Step 2: Generate embeddings
        logger.info("🧠 Step 2: Generating embeddings...")
        embeddings_start = time.time()
        
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = self._generate_embeddings_fast(texts)
        
        embeddings_time = time.time() - embeddings_start
        logger.info(f"✅ Generated {len(embeddings)} embeddings in {embeddings_time:.2f}s")
        
        # Step 3: Build FAISS index
        logger.info("🔍 Step 3: Building FAISS index...")
        faiss_start = time.time()
        
        embeddings_array = np.array(embeddings).astype('float32')
        self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product for cosine similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings_array)
        self.index.add(embeddings_array)
        
        faiss_time = time.time() - faiss_start
        logger.info(f"✅ FAISS index built in {faiss_time:.2f}s")
        
        # Store data
        self.chunks = all_chunks
        self.embeddings = embeddings
        self.ready = True
        self.last_updated = datetime.now().isoformat()
        
        # 🚀 Save to Memcache + GCS instead of disk
        self._save_to_cache_and_gcs()
        
        total_time = time.time() - total_start
        logger.info(f"🎉 Processing complete in {total_time:.2f}s")
        logger.info(f"📊 Ready for semantic search: {len(self.chunks)} chunks")
    
    async def search_similar(self, query: str, max_results: int = 5) -> List[Dict]:
        """Ultra fast semantic search using FAISS"""
        if not self.ready:
            self._load_from_cache_or_gcs()
        
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
            
            # FAISS search
            scores, indices = self.index.search(query_embedding, max_results)
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx].copy()
                    chunk['relevance_score'] = float(score)
                    results.append(chunk)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    async def process_query(self, question: str, max_results: int = 5) -> Dict:
        """Process user query using semantic search + LLM"""
        logger.info(f"🔍 Processing query: '{question[:50]}...'")
        
        # Get semantically relevant context
        context_results = await self.search_similar(question, max_results)
        
        if not context_results:
            return {
                "answer": "I don't have information about that topic in my knowledge base.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Prepare context for LLM
        context_text = ""
        sources = []
        
        for result in context_results:
            context_text += f"Source: {result['metadata']['title']}\n"
            context_text += f"URL: {result['metadata']['source_url']}\n"
            context_text += f"Content: {result['text']}\n\n"
            
            sources.append({
                "url": result['metadata']['source_url'],
                "title": result['metadata']['title'],
                "relevance_score": result['relevance_score']
            })
        
        # Generate response using Gemini

        if not self.google_api_key:
            return {
                "answer": "I'm here to help, but I'm having trouble accessing our knowledge base right now. Let me try to assist you with the information I have available: " + context_results[0]['text'][:200] + "... Would you like me to try again or can I help you with something else?",
                "sources": sources,
                "confidence": context_results[0]['relevance_score'] if context_results else 0.0
            }

        try:
            # Improved prompt that makes the AI act as a business representative
            prompt = f"""You are an intelligent AI assistant representing this business and helping their customers. You have access to the company's knowledge base and should respond as a helpful, professional representative of this business.

CONTEXT FROM KNOWLEDGE BASE:
{context_text}

CUSTOMER QUESTION: {question}

RULES:
- You are a knowledgeable sales representative of this business
- Be friendly and professional
- Use only the provided context
- Keep responses concise (2-3 sentences max)
- If context is incomplete, briefly explain what you know and ask one clarifying question
- Never copy large text chunks - summarize naturally
- Present information as if you're explaining it from your expertise, not reading from documents

Response:"""
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.google_api_key}",
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,  # Slightly more creative for conversational tone
                            "topP": 0.8,
                            "topK": 40,
                            "maxOutputTokens": 1024,
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Calculate average confidence
                    avg_confidence = sum(r['relevance_score'] for r in context_results) / len(context_results)
                    
                    return {
                        "answer": answer,
                        "sources": sources,
                        "confidence": avg_confidence
                    }
                else:
                    logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                    return {
                        "answer": "I'm here to help! I found some relevant information in our knowledge base, but I'm having a small technical issue right now. Let me share what I can: " + context_results[0]['text'][:300] + "... Can you let me know more specifically what you're looking for so I can better assist you?",
                        "sources": sources,
                        "confidence": context_results[0]['relevance_score']
                    }
                    
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            fallback_message = "I'm experiencing a technical issue right now, but I'm here to help! "
            
            if context_results:
                # Provide a more conversational fallback with available context
                fallback_message += f"I can see we have information about your question. {context_results[0]['text'][:200]}... Would you like to try asking your question differently, or is there something specific I can help clarify?"
            else:
                fallback_message += "Could you please rephrase your question or let me know more details about what you're looking for? I want to make sure I give you the most helpful information."
            
            return {
                "answer": fallback_message,
                "sources": sources,
                "confidence": context_results[0]['relevance_score'] if context_results else 0.0
            }
    
    def _create_chunks(self, page: Dict) -> List[Dict]:
        """Create chunks from page content"""
        try:
            content = page.get('content', '')
            if not content:
                return []
            
            chunks = []
            sentences = content.split('. ')
            
            current_chunk = ""
            max_chunk_size = 500  # characters
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) + 2 <= max_chunk_size:
                    current_chunk += sentence + ". "
                else:
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
                    current_chunk = sentence + ". "
            
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
    
    def _generate_embeddings_fast(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings with speed optimizations"""
        logger.info(f"   🔄 Processing {len(texts)} texts in batches of {self.batch_size}")
        
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            batch_embeddings = self.model.encode(
                batch,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            
            all_embeddings.extend(batch_embeddings.tolist())
            
            if (i + self.batch_size) % 100 == 0:
                logger.info(f"   ⚡ Processed {min(i + self.batch_size, len(texts))}/{len(texts)} texts")
        
        return all_embeddings
    
    def is_ready(self) -> bool:
        """Check if vector store is ready for queries"""
        if not self.ready:
            self._load_from_cache_or_gcs()
        return self.ready and len(self.chunks) > 0
    
    def get_total_chunks(self) -> int:
        """Get total number of chunks in vector store"""
        return len(self.chunks)
    
    def clear_data(self):
        """Clear all data from this vector store"""
        try:
            # Clear memory
            self.chunks = []
            self.embeddings = None
            self.index = None
            self.ready = False
            self.last_updated = None
            
            # Clear cache
            self.invalidate_cache()
            
            # Optionally clear GCS (commented out for safety)
            # self._delete_from_gcs()
            
            logger.info(f"🗑️ Cleared all data for {self.user_id}/{self.knowledge_base_id}")
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")

    async def process_document(self, document_data: dict) -> int:
        """Process a single document and add it to the vector store"""
        try:
            text_content = document_data.get('text', '')
            metadata = document_data.get('metadata', {})

            if not text_content.strip():
                return 0

            # Load model if not already loaded
            self._load_model()

            # Create a page-like structure for the _create_chunks method
            page_structure = {
                'content': text_content,
                'url': metadata.get('source_url', 'uploaded_file'),
                'title': metadata.get('title', 'Uploaded Document'),
                'scraped_at': metadata.get('uploaded_at', datetime.now().isoformat())
            }

            # Use existing _create_chunks method
            chunks = self._create_chunks(page_structure)

            if not chunks:
                return 0

            # Generate embeddings for the new chunks
            texts = [chunk['text'] for chunk in chunks]
            new_embeddings = self._generate_embeddings_fast(texts)

            if not new_embeddings:
                return 0

            # Add to existing data
            self.chunks.extend(chunks)

            # Handle embeddings
            if self.embeddings is None:
                self.embeddings = new_embeddings
            else:
                self.embeddings.extend(new_embeddings)

            # Rebuild FAISS index with all embeddings
            embeddings_array = np.array(self.embeddings).astype('float32')

            # Create new index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product for cosine similarity

            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings_array)
            self.index.add(embeddings_array)

            # Update metadata
            self.ready = True
            self.last_updated = datetime.now().isoformat()

            # 🚀 Save to Memcache + GCS
            self._save_to_cache_and_gcs()

            logger.info(f"Added {len(chunks)} chunks from document: {metadata.get('title', 'Unknown')}")

            return len(chunks)

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return 0

# Alias for backward compatibility
SaaSVectorStore = MemcacheGCSVectorStore
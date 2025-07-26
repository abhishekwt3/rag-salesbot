# saas_embeddings.py - Multi-tenant Vector Store with Memcache + S3
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

# Memcache and S3 clients
import pymemcache.client.base
import pymemcache.serde
import pickle
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class MemcacheS3VectorStore:
    """Multi-tenant vector store using Memcache + S3 backend"""
    
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
        
        # 🚀 Memcache + S3 Configuration
        self._setup_clients()
        
        # Cache keys for this knowledge base
        self.cache_prefix = f"embeddings:{user_id}:{knowledge_base_id}"
        self.chunks_key = f"{self.cache_prefix}:chunks"
        self.faiss_key = f"{self.cache_prefix}:faiss"
        self.metadata_key = f"{self.cache_prefix}:metadata"
        
        # S3 paths for this knowledge base
        self.s3_prefix = f"embeddings/{user_id}/{knowledge_base_id}"
        self.s3_chunks_key = f"{self.s3_prefix}/chunks.json.gz"
        self.s3_faiss_key = f"{self.s3_prefix}/faiss_index.bin"
        self.s3_metadata_key = f"{self.s3_prefix}/metadata.json"
        
        # Google API key for LLM responses
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not found in environment")
        
        # Load existing data if available
        self._load_from_cache_or_s3()
    
    def _setup_clients(self):
        """Setup Memcache and S3 clients"""
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
            # S3 client
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'ap-south-1')
            )
            
            self.s3_bucket = os.getenv('S3_EMBEDDINGS_BUCKET', 'your-embeddings-bucket')
            
            # Test S3 connection
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            logger.info(f"✅ Connected to S3 bucket: {self.s3_bucket}")
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to S3: {e}")
            self.s3_client = None
    
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
    
    def _save_to_cache_and_s3(self):
        """Save embeddings and index to Memcache + S3"""
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
            
            # 💾 Save to S3 (persistent, for durability)
            s3_success = self._save_to_s3(chunks_data, metadata)
            
            save_time = time.time() - save_start
            
            if cache_success and s3_success:
                logger.info(f"💾 Saved {len(self.chunks)} chunks to Memcache + S3 in {save_time:.2f}s")
            elif cache_success:
                logger.warning(f"⚠️ Saved to Memcache only (S3 failed) in {save_time:.2f}s")
            elif s3_success:
                logger.warning(f"⚠️ Saved to S3 only (Memcache failed) in {save_time:.2f}s")
            else:
                logger.error(f"❌ Failed to save to both Memcache and S3")
            
        except Exception as e:
            logger.error(f"Error saving to cache and S3: {e}")
    
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
    
    def _save_to_s3(self, chunks_data: dict, metadata: dict) -> bool:
        """Save data to S3"""
        if not self.s3_client:
            return False
        
        try:
            # Save compressed chunks data
            chunks_json = json.dumps(chunks_data).encode('utf-8')
            compressed_chunks = self._compress_data(chunks_json)
            
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=self.s3_chunks_key,
                Body=compressed_chunks,
                ContentType='application/gzip',
                Metadata={
                    'user-id': self.user_id,
                    'knowledge-base-id': self.knowledge_base_id,
                    'total-chunks': str(len(self.chunks))
                }
            )
            
            # Save FAISS index if available
            if self.index:
                faiss_data = faiss.serialize_index(self.index)
                faiss_bytes = faiss_data.tobytes() if hasattr(faiss_data, 'tobytes') else bytes(faiss_data)
                self.s3_client.put_object(
                    Bucket=self.s3_bucket,
                    Key=self.s3_faiss_key,
                    Body=faiss_bytes,
                    ContentType='application/octet-stream'
                )
            
            # Save metadata
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=self.s3_metadata_key,
                Body=json.dumps(metadata).encode('utf-8'),
                ContentType='application/json'
            )
            
            logger.debug(f"✅ Saved to S3: {self.s3_prefix}")
            return True
            
        except Exception as e:
            logger.error(f"❌ S3 save error: {e}")
            return False
    
    def _load_from_cache_or_s3(self):
        """Load embeddings and index from Memcache or S3"""
        try:
            load_start = time.time()
            # Try Memcache first (fast path)
            logger.info("🔍 Checking Memcache for existing data...")
            if self._load_from_memcache():
                load_time = time.time() - load_start
                logger.info(f"⚡ MEMCACHE HIT: Loaded {len(self.chunks)} chunks in {load_time:.3f}s (FAST PATH)")
                return
            logger.info("❌ Memcache miss - falling back to S3...")
            
            # Fallback to S3 (slower but persistent)
            if self._load_from_s3():
                s3_load_time = time.time() - load_start
                logger.info(f"📁 S3 FALLBACK: Loaded {len(self.chunks)} chunks in {s3_load_time:.3f}s (SLOW PATH)")
                # Cache in Memcache for next time
                self._cache_in_memcache()
                logger.info("💾 Cached S3 data to Memcache for faster future access")
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
            
        except Exception as e:
            logger.error(f"❌ Memcache load error: {e}")
            return False
    
    def _load_from_s3(self) -> bool:
        """Load data from S3"""
        if not self.s3_client:
            return False
        
        try:
            # Load chunks data
            response = self.s3_client.get_object(
                Bucket=self.s3_bucket,
                Key=self.s3_chunks_key
            )
            
            compressed_data = response['Body'].read()
            decompressed_data = self._decompress_data(compressed_data)
            chunks_data = json.loads(decompressed_data.decode('utf-8'))
            
            self.chunks = chunks_data.get('chunks', [])
            self.embeddings = chunks_data.get('embeddings', [])
            self.last_updated = chunks_data.get('last_updated')
            self.ready = chunks_data.get('ready', False)
            
            # Load FAISS index
            try:
                faiss_response = self.s3_client.get_object(
                    Bucket=self.s3_bucket,
                    Key=self.s3_faiss_key
                )
                faiss_bytes = faiss_response['Body'].read()
                faiss_data = np.frombuffer(faiss_bytes, dtype=np.uint8)
                self.index = faiss.deserialize_index(faiss_data)
            except ClientError:
                logger.debug("No FAISS index found in S3, will rebuild")
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                logger.debug(f"No S3 data found for {self.s3_prefix}")
            else:
                logger.error(f"❌ S3 load error: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ S3 load error: {e}")
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
        
        # 🚀 Save to Memcache + S3 instead of disk
        self._save_to_cache_and_s3()
        
        total_time = time.time() - total_start
        logger.info(f"🎉 Processing complete in {total_time:.2f}s")
        logger.info(f"📊 Ready for semantic search: {len(self.chunks)} chunks")
    
    async def search_similar(self, query: str, max_results: int = 5) -> List[Dict]:
        """Ultra fast semantic search using FAISS"""
        if not self.ready:
            self._load_from_cache_or_s3()
        
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

INSTRUCTIONS:
🎯 ROLE & PERSONALITY:
- You are a knowledgeable representative of this business
- Be helpful, professional, and genuinely interested in solving the customer's needs
- Show enthusiasm about the company's products/services when appropriate
- Use a conversational, friendly tone while maintaining professionalism

📚 KNOWLEDGE BASE USAGE:
- Use the provided context to answer accurately and helpfully
- NEVER copy/paste large chunks of text from the knowledge base
- Synthesize information into natural, conversational responses
- If you need to reference specific details, paraphrase them naturally
- Present information as if you're explaining it from your expertise, not reading from documents

🤝 ENGAGEMENT STRATEGY:
- If the context fully answers the question: Provide a complete, helpful response
- If the context is incomplete: Give what information you can, then ask relevant follow-up questions to better help them
- If the context is unclear about their specific needs: Ask clarifying questions to understand exactly what they're looking for
- Always try to be proactive - suggest related information that might be helpful

❌ IMPORTANT LIMITATIONS:
- Only use information from the provided context
- If the context doesn't contain relevant information, politely say so and offer to help with related topics you do have information about
- Never make up or assume information not in the context
- Don't expose raw document content or internal formatting

💬 RESPONSE FORMAT:
- Start with a direct answer if possible
- Add helpful context or explanations
- End with a follow-up question or offer for additional help when appropriate
- Keep responses conversational and naturally flowing

EXAMPLES OF GOOD RESPONSES:
- "Great question! Based on our offerings, [synthesized answer]. Would you like me to explain more about [related topic] or do you have specific requirements I can help you with?"
- "I can help you with that. [Answer from context]. What's your specific use case so I can provide more targeted recommendations?"
- "That's something we definitely cover. [Natural explanation]. Are you looking at this for [likely scenario] or do you have a different situation in mind?"

Now, respond to the customer's question as a helpful business representative:"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.google_api_key}",
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
            self._load_from_cache_or_s3()
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
            
            # Optionally clear S3 (commented out for safety)
            # self._delete_from_s3()
            
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

            # 🚀 Save to Memcache + S3
            self._save_to_cache_and_s3()

            logger.info(f"Added {len(chunks)} chunks from document: {metadata.get('title', 'Unknown')}")

            return len(chunks)

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return 0

# Alias for backward compatibility
SaaSVectorStore = MemcacheS3VectorStore
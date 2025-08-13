# saas_embeddings.py - Multi-tenant Vector Store with Google Embeddings + ChromaDB
import os
import json
import time
import gzip
from typing import List, Dict, Optional
from datetime import datetime
import logging
from pathlib import Path
import uuid

# Google Embedding API
import google.generativeai as genai
import httpx

# ChromaDB for vector storage
import chromadb
from chromadb.config import Settings

# Memcache client (keeping existing cache system)
import pymemcache.client.base
import pymemcache.serde
import pickle

logger = logging.getLogger(__name__)

class MemcacheS3VectorStore:
    """Multi-tenant vector store using Google Embeddings + ChromaDB with Memcache + S3 backend"""
    
    def __init__(self, user_id: str, knowledge_base_id: str, model_name: str = "models/embedding-001"):
        """Initialize with user and knowledge base IDs"""
        self.user_id = user_id
        self.knowledge_base_id = knowledge_base_id
        self.model_name = model_name
        self.chunks = []
        self.ready = False
        self.last_updated = None
        
        # Speed optimizations
        self.batch_size = 32  # Process in batches for speed
        
        # 🚀 Google Embedding API setup
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=self.google_api_key)
        
        # 🗄️ ChromaDB setup
        self.collection_name = f"kb_{user_id}_{knowledge_base_id}".replace('-', '_')
        self._setup_chromadb()
        
        # 🚀 Memcache Configuration (keeping existing cache)
        self._setup_clients()
        
        # Cache keys for this knowledge base
        self.cache_prefix = f"embeddings:{user_id}:{knowledge_base_id}"
        self.chunks_key = f"{self.cache_prefix}:chunks"
        self.metadata_key = f"{self.cache_prefix}:metadata"
        
        # Google API key for LLM responses
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not found in environment")
        
        # Load existing data
        self._load_from_cache()
    
    def _setup_chromadb(self):
        """Initialize ChromaDB client and collection"""
        try:
            # Use persistent client for data durability
            persist_dir = f"./chroma_data/{self.user_id}/{self.knowledge_base_id}"
            os.makedirs(persist_dir, exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(
                path=persist_dir,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=self.collection_name
                )
                logger.info(f"✅ Connected to existing ChromaDB collection: {self.collection_name}")
            except Exception:
                self.collection = self.chroma_client.create_collection(
                    name=self.collection_name,
                    metadata={"description": f"Knowledge base {self.knowledge_base_id} for user {self.user_id}"}
                )
                logger.info(f"✅ Created new ChromaDB collection: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"❌ ChromaDB setup failed: {e}")
            raise
    
    def _setup_clients(self):
        """Setup Memcache client"""
        # Memcache setup
        try:
            memcache_host = os.getenv('MEMCACHE_HOST', 'localhost:11211')
            self.memcache = pymemcache.client.base.Client(
                (memcache_host.split(':')[0], int(memcache_host.split(':')[1])),
                serializer=pymemcache.serde.pickle_serde,
                connect_timeout=5,
                timeout=10
            )
            logger.info(f"✅ Memcache connected: {memcache_host}")
        except Exception as e:
            logger.warning(f"⚠️ Memcache connection failed: {e}")
            self.memcache = None
    
    async def _generate_embeddings_google(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Google Embedding API"""
        logger.info(f"🔄 Processing {len(texts)} texts with Google Embedding API in batches of {self.batch_size}")
        
        all_embeddings = []
        
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                # Generate embeddings for batch
                batch_embeddings = []
                for text in batch:
                    result = genai.embed_content(
                        model=self.model_name,
                        content=text,
                        task_type="retrieval_document"
                    )
                    batch_embeddings.append(result['embedding'])
                
                all_embeddings.extend(batch_embeddings)
                
                if (i + self.batch_size) % 100 == 0:
                    logger.info(f"   ⚡ Processed {min(i + self.batch_size, len(texts))}/{len(texts)} texts")
                
                # Rate limiting for API
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Google Embedding API error for batch {i}: {e}")
                # Add zero embeddings for failed batch to maintain indexing
                batch_embeddings = [[0.0] * 768 for _ in batch]  # Google embeddings are 768-dim
                all_embeddings.extend(batch_embeddings)
        
        return all_embeddings
    
    async def process_pages(self, pages: List[Dict]):
        """Process pages with Google Embeddings + ChromaDB"""
        logger.info(f"🚀 Google Embeddings + ChromaDB processing for {len(pages)} pages...")
        total_start = time.time()
        
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
        
        # Step 2: Generate embeddings with Google API
        logger.info("🧠 Step 2: Generating embeddings with Google API...")
        embeddings_start = time.time()
        
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = await self._generate_embeddings_google(texts)
        
        embeddings_time = time.time() - embeddings_start
        logger.info(f"✅ Generated {len(embeddings)} embeddings in {embeddings_time:.2f}s")
        
        # Step 3: Store in ChromaDB
        logger.info("💾 Step 3: Storing in ChromaDB...")
        storage_start = time.time()
        
        # Clear existing collection data
        try:
            self.collection.delete()
            logger.info("🗑️ Cleared existing collection data")
        except Exception as e:
            logger.debug(f"Collection clear info: {e}")
        
        # Prepare data for ChromaDB
        documents = [chunk['text'] for chunk in all_chunks]
        metadatas = [chunk['metadata'] for chunk in all_chunks]
        ids = [str(uuid.uuid4()) for _ in all_chunks]
        
        # Add to ChromaDB
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        
        storage_time = time.time() - storage_start
        logger.info(f"✅ Stored in ChromaDB in {storage_time:.2f}s")
        
        # Update instance data
        self.chunks = all_chunks
        self.ready = True
        self.last_updated = datetime.now().isoformat()
        
        # 🚀 Save to Memcache
        self._save_to_cache()
        
        total_time = time.time() - total_start
        logger.info(f"🎉 TOTAL PROCESSING TIME: {total_time:.2f}s for {len(all_chunks)} chunks")
    
    async def semantic_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using ChromaDB"""
        if not self.ready:
            logger.warning("Vector store not ready")
            return []
        
        try:
            # Generate query embedding with Google API
            query_result = genai.embed_content(
                model=self.model_name,
                content=query,
                task_type="retrieval_query"
            )
            query_embedding = query_result['embedding']
            
            # Search ChromaDB
            search_start = time.time()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                include=["documents", "metadatas", "distances"]
            )
            search_time = time.time() - search_start
            
            logger.info(f"🔍 ChromaDB search completed in {search_time*1000:.1f}ms")
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    formatted_results.append({
                        'text': doc,
                        'metadata': metadata,
                        'score': 1.0 - distance  # Convert distance to similarity score
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    async def process_document(self, document_data: dict) -> int:
        """Process a single document and add it to the vector store"""
        try:
            text_content = document_data.get('text', '')
            metadata = document_data.get('metadata', {})

            if not text_content.strip():
                return 0

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
            new_embeddings = await self._generate_embeddings_google(texts)

            if not new_embeddings:
                return 0

            # Add to ChromaDB
            documents = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [str(uuid.uuid4()) for _ in chunks]
            
            self.collection.add(
                documents=documents,
                embeddings=new_embeddings,
                metadatas=metadatas,
                ids=ids
            )

            # Add to existing data
            self.chunks.extend(chunks)

            # Update metadata
            self.ready = True
            self.last_updated = datetime.now().isoformat()

            # 🚀 Save to Memcache
            self._save_to_cache()

            logger.info(f"Added {len(chunks)} chunks from document: {metadata.get('title', 'Unknown')}")

            return len(chunks)

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return 0

    def clear_data(self):
        """Clear all data from this vector store"""
        try:
            # Clear ChromaDB collection
            try:
                self.collection.delete()
                logger.info("🗑️ Cleared ChromaDB collection")
            except Exception as e:
                logger.debug(f"ChromaDB clear info: {e}")
            
            # Clear memory
            self.chunks = []
            self.ready = False
            self.last_updated = None
            
            # Clear Memcache
            if self.memcache:
                try:
                    self.memcache.delete(self.chunks_key)
                    self.memcache.delete(self.metadata_key)
                    logger.info(f"🗑️ Cleared Memcache for {self.cache_prefix}")
                except Exception as e:
                    logger.error(f"Error clearing Memcache: {e}")
            
            logger.info(f"🗑️ Cleared all data for {self.user_id}/{self.knowledge_base_id}")
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")

    async def add_document(self, document_data: Dict) -> int:
        """Add a single document to the knowledge base"""
        try:
            logger.info(f"📄 Adding document: {document_data.get('filename', 'Unknown')}")

            # Create page structure for compatibility
            page_structure = {
                'content': document_data.get('content', ''),
                'url': document_data.get('filename', ''),
                'title': document_data.get('filename', ''),
                'scraped_at': datetime.now().isoformat()
            }

            # Use existing _create_chunks method
            chunks = self._create_chunks(page_structure)

            if not chunks:
                return 0

            # Generate embeddings for the new chunks
            texts = [chunk['text'] for chunk in chunks]
            new_embeddings = await self._generate_embeddings_google(texts)

            if not new_embeddings:
                return 0

            # Add to ChromaDB
            documents = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [str(uuid.uuid4()) for _ in chunks]
            
            self.collection.add(
                documents=documents,
                embeddings=new_embeddings,
                metadatas=metadatas,
                ids=ids
            )

            # Add to existing data
            self.chunks.extend(chunks)

            # Update metadata
            self.ready = True
            self.last_updated = datetime.now().isoformat()

            # 🚀 Save to Memcache
            self._save_to_cache()

            logger.info(f"Added {len(chunks)} chunks from document: {document_data.get('filename', 'Unknown')}")

            return len(chunks)

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return 0
    
    def _create_chunks(self, page: Dict) -> List[Dict]:
        """Create chunks from page content (keeping existing implementation)"""
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
                if len(current_chunk) + len(sentence) > 800:  # Optimal chunk size
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
                    current_chunk = sentence + ". "
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

    
    def _save_to_cache(self):
        """Save chunks metadata to Memcache (ChromaDB handles embeddings)"""
        try:
            save_start = time.time()
            
            # Prepare metadata for storage (no need to store embeddings as ChromaDB handles that)
            chunks_data = {
                'chunks': self.chunks,
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
            
            save_time = time.time() - save_start
            
            if cache_success:
                logger.info(f"💾 Saved {len(self.chunks)} chunks metadata to Memcache in {save_time:.2f}s")
            else:
                logger.error(f"❌ Failed to save to Memcache")
            
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def _save_to_memcache(self, chunks_data: dict, metadata: dict) -> bool:
        """Save data to Memcache"""
        if not self.memcache:
            return False
        
        try:
            # Cache with 1 hour TTL
            ttl = 3600
            self.memcache.set(self.chunks_key, chunks_data, expire=ttl)
            self.memcache.set(self.metadata_key, metadata, expire=ttl)
            
            logger.debug(f"✅ Saved to Memcache: {self.cache_prefix}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Memcache save error: {e}")
            return False
    
    def _load_from_cache(self):
        """Load chunks from Memcache or fallback to ChromaDB"""
        try:
            load_start = time.time()
            # Try Memcache first
            logger.info("🔍 Checking Memcache for existing data...")
            if self._load_from_memcache():
                load_time = time.time() - load_start
                logger.info(f"⚡ MEMCACHE HIT: Loaded {len(self.chunks)} chunks in {load_time:.3f}s")
                return
            
            logger.info("❌ Memcache miss - checking ChromaDB...")
            
            # Fallback to ChromaDB (the actual database)
            if self._load_from_chromadb():
                db_load_time = time.time() - load_start
                logger.info(f"📊 CHROMADB FALLBACK: Loaded {len(self.chunks)} chunks in {db_load_time:.3f}s")
                # Cache in Memcache for next time
                self._cache_in_memcache()
                logger.info("💾 Cached ChromaDB data to Memcache for faster future access")
                return
            
            logger.info(f"📁 No existing data found for {self.user_id}/{self.knowledge_base_id}")
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    def _load_from_memcache(self) -> bool:
        """Load data from Memcache"""
        if not self.memcache:
            return False
        
        try:
            # Load chunks
            chunks_data = self.memcache.get(self.chunks_key)
            if not chunks_data:
                return False
            
            self.chunks = chunks_data.get('chunks', [])
            self.last_updated = chunks_data.get('last_updated')
            self.ready = chunks_data.get('ready', False)
            
            logger.debug(f"✅ Loaded from Memcache: {len(self.chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"❌ Memcache load error: {e}")
            return False
    
    def _load_from_chromadb(self) -> bool:
        """Load chunks metadata from ChromaDB when Memcache fails"""
        try:
            # Check if ChromaDB collection has data
            count = self.collection.count()
            if count == 0:
                return False
            
            # Get all documents and metadata from ChromaDB
            results = self.collection.get(
                include=["documents", "metadatas"]
            )
            
            if not results['documents']:
                return False
            
            # Rebuild chunks list from ChromaDB data
            self.chunks = []
            for doc, metadata in zip(results['documents'], results['metadatas']):
                self.chunks.append({
                    'text': doc,
                    'metadata': metadata
                })
            
            self.ready = True
            self.last_updated = datetime.now().isoformat()
            
            logger.debug(f"✅ Loaded from ChromaDB: {len(self.chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"❌ ChromaDB load error: {e}")
            return False
    
    def _cache_in_memcache(self):
        """Cache current data in Memcache after ChromaDB load"""
        if not self.memcache:
            return
        
        chunks_data = {
            'chunks': self.chunks,
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
        
        self._save_to_memcache(chunks_data, metadata)

    
    async def process_query(self, question: str, max_results: int = 5) -> Dict:
        """Process a query and return answer with sources"""
        if not self.ready:
            return {
                "answer": "Knowledge base is not ready. Please process some content first.",
                "sources": [],
                "confidence": 0.0
            }
        
        try:
            # Get relevant chunks
            relevant_chunks = await self.semantic_search(question, max_results)
            
            if not relevant_chunks:
                return {
                    "answer": "I couldn't find relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Prepare context for LLM
            context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
            sources = [chunk['metadata'] for chunk in relevant_chunks]
            
            # Generate answer using Google's Gemini API
            answer = await self._generate_answer_google(question, context)
            
            return {
                "answer": answer,
                "sources": sources,
                "confidence": 0.8  # Default confidence
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "answer": "Sorry, I encountered an error processing your question.",
                "sources": [],
                "confidence": 0.0
            }
    
    async def _generate_answer_google(self, question: str, context: str) -> str:
        """Generate answer using Google's Gemini API"""
        try:
            # Use Gemini for text generation
            model = genai.GenerativeModel('gemini-2.0-flash')

            prompt = f"""You are a helpful sales assistant. Based on the following information, concisely answer the customer's question and focus on how our features can help them.

Information:
{context}

Customer Question: {question}

Answer as a knowledgeable sales assistant. If you don't have the specific information needed, say you'll get back to them."""

            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating answer with Google API: {e}")
            return "I'll get back to you with that information. Please try again."
    
    def is_ready(self) -> bool:
        """Check if vector store is ready for queries"""
        if not self.ready:
            # Try to load from cache if not already loaded
            self._load_from_cache()
        
        # Also check if ChromaDB collection has data
        try:
            count = self.collection.count()
            return self.ready and count > 0
        except Exception:
            return self.ready and len(self.chunks) > 0
    
    def get_total_chunks(self) -> int:
        """Get total number of chunks"""
        try:
            return self.collection.count()
        except Exception:
            return len(self.chunks)

# Test functions for connections
def test_google_embeddings():
    """Simple test for Google Embedding API connection"""
    try:
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in environment")
            return False
        
        genai.configure(api_key=api_key)
        
        # Test embedding generation
        result = genai.embed_content(
            model="models/embedding-001",
            content="This is a test sentence for Google Embeddings API.",
            task_type="retrieval_document"
        )
        
        embedding = result['embedding']
        print(f"✅ Google Embeddings API connected successfully!")
        print(f"   📏 Embedding dimension: {len(embedding)}")
        print(f"   🔢 Sample values: {embedding[:5]}")
        return True
        
    except Exception as e:
        print(f"❌ Google Embeddings API test failed: {e}")
        return False

def test_chromadb():
    """Simple test for ChromaDB connection"""
    try:
        # Test persistent client
        test_dir = "./chroma_test"
        os.makedirs(test_dir, exist_ok=True)
        
        client = chromadb.PersistentClient(
            path=test_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create test collection
        collection_name = f"test_collection_{int(time.time())}"
        collection = client.create_collection(name=collection_name)
        
        # Test add and query
        collection.add(
            documents=["This is a test document"],
            ids=["test-1"],
            metadatas=[{"source": "test"}]
        )
        
        results = collection.query(
            query_texts=["test document"],
            n_results=1
        )
        
        print(f"✅ ChromaDB connected successfully!")
        print(f"   📊 Collection created: {collection_name}")
        print(f"   🔍 Query results: {len(results['documents'][0])} documents found")
        
        # Cleanup
        client.delete_collection(collection_name)
        import shutil
        shutil.rmtree(test_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB test failed: {e}")
        return False

# Alias for backward compatibility
SaaSVectorStore = MemcacheS3VectorStore

if __name__ == "__main__":
    print("🧪 Testing connections...")
    print("\n1. Testing Google Embeddings API:")
    test_google_embeddings()
    
    print("\n2. Testing ChromaDB:")
    test_chromadb()
    
    print("\n✅ Connection tests completed!")
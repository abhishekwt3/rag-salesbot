# saas_embeddings.py - Multi-tenant Vector Store for SaaS
import os
import json
import time
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
import logging
from pathlib import Path

# Fast sentence transformers
from sentence_transformers import SentenceTransformer
import faiss  # Ultra fast similarity search
import httpx

logger = logging.getLogger(__name__)

class SaaSVectorStore:
    """Multi-tenant vector store for SaaS application"""
    
    def __init__(self, storage_dir: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize with user-specific storage directory"""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
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
        self.cache_file = self.storage_dir / "embeddings_cache.json"
        self.faiss_index_file = self.storage_dir / "faiss_index.bin"
        
        # Google API key for LLM responses
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not found in environment")
        
        # Load existing data if available
        self._load_from_disk()
    
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
        
        # Save to disk
        self._save_to_disk()
        
        total_time = time.time() - total_start
        logger.info(f"🎉 Processing complete in {total_time:.2f}s")
        logger.info(f"📊 Ready for semantic search: {len(self.chunks)} chunks")
    
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
    
    async def search_similar(self, query: str, max_results: int = 5) -> List[Dict]:
        """Ultra fast semantic search using FAISS"""
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
                "answer": "LLM service not available. Here's the most relevant content: " + context_results[0]['text'],
                "sources": sources,
                "confidence": context_results[0]['relevance_score'] if context_results else 0.0
            }
        
        try:
            prompt = f"""Based on the following context, answer the user's question accurately and concisely.

Context:
{context_text}

Question: {question}

Instructions:
- Only use information from the provided context
- If the context doesn't contain relevant information, say so
- Provide a clear, helpful answer
- Don't make up information

Answer:"""

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.google_api_key}",
                    json={
                        "contents": [{
                            "parts": [{"text": prompt}]
                        }]
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
                        "answer": f"I found relevant information in your knowledge base, but I'm having trouble generating a response right now. Here's what I found: {context_results[0]['text'][:500]}...",
                        "sources": sources,
                        "confidence": context_results[0]['relevance_score']
                    }
                    
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return {
                "answer": f"I found relevant information about your question, but I'm having trouble generating a response right now. Here's what I found in your knowledge base: {context_results[0]['text'][:500]}..." if context_results else "I'm having trouble processing your question right now.",
                "sources": sources,
                "confidence": context_results[0]['relevance_score'] if context_results else 0.0
            }
    
    def _save_to_disk(self):
        """Save embeddings and index to user-specific directory"""
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
                faiss.write_index(self.index, str(self.faiss_index_file))
            
            logger.info(f"💾 Saved {len(self.chunks)} chunks to {self.storage_dir}")
            
        except Exception as e:
            logger.error(f"Error saving to disk: {e}")
    
    def _load_from_disk(self):
        """Load embeddings and index from user-specific directory"""
        try:
            # Load chunks and metadata
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    self.chunks = data.get('chunks', [])
                    self.embeddings = data.get('embeddings', [])
                    self.last_updated = data.get('last_updated')
                    self.ready = data.get('ready', False)
            
            # Load FAISS index
            if self.faiss_index_file.exists():
                self.index = faiss.read_index(str(self.faiss_index_file))
            
            if self.chunks:
                logger.info(f"📁 Loaded {len(self.chunks)} chunks from {self.storage_dir}")
            
        except FileNotFoundError:
            logger.info(f"📁 No existing cache found in {self.storage_dir}")
        except Exception as e:
            logger.error(f"Error loading from disk: {e}")
    
    def is_ready(self) -> bool:
        """Check if vector store is ready for queries"""
        if not self.ready:
            self._load_from_disk()
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
            
            # Clear files
            if self.cache_file.exists():
                self.cache_file.unlink()
            if self.faiss_index_file.exists():
                self.faiss_index_file.unlink()
            
            logger.info(f"🗑️ Cleared all data from {self.storage_dir}")
            
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
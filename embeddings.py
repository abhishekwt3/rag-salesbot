# embeddings.py - Fixed with proper imports
import os
import tiktoken
from typing import List, Dict, Optional
from datetime import datetime
import re

import openai
import chromadb
from chromadb.config import Settings

class EmbeddingManager:
    def __init__(self):
        # Initialize OpenAI
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.client = openai.OpenAI()
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(
            name="website_content",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Tokenizer for chunk sizing
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        self.chunk_size = 500  # tokens
        self.chunk_overlap = 50  # tokens
        self.ready = False
        self.last_updated = None
    
    async def process_and_embed(self, pages: List[Dict]):
        """Process pages into chunks and create embeddings"""
        all_chunks = []
        
        for page in pages:
            chunks = self._create_chunks(page)
            all_chunks.extend(chunks)
        
        # Create embeddings in batches
        batch_size = 100
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i:i + batch_size]
            await self._embed_batch(batch)
        
        self.ready = True
        self.last_updated = datetime.now().isoformat()
        
        print(f"Processed {len(all_chunks)} chunks from {len(pages)} pages")
    
    def _create_chunks(self, page: Dict) -> List[Dict]:
        """Split page content into overlapping chunks"""
        content = page['content']
        tokens = self.tokenizer.encode(content)
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'source_url': page['url'],
                    'title': page['title'],
                    'chunk_index': len(chunks),
                    'scraped_at': page['scraped_at'],
                    'word_count': len(chunk_text.split())
                }
            })
            
            start = end - self.chunk_overlap
        
        return chunks
    
    async def _embed_batch(self, chunks: List[Dict]):
        """Create embeddings for a batch of chunks"""
        texts = [chunk['text'] for chunk in chunks]
        
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            
            # Store in ChromaDB
            ids = [f"chunk_{datetime.now().timestamp()}_{i}" for i in range(len(chunks))]
            metadatas = [chunk['metadata'] for chunk in chunks]
            documents = texts
            
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
            
        except Exception as e:
            print(f"Error creating embeddings: {e}")
            raise
    
    async def search_similar(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search for similar content using query embedding"""
        
        # Create query embedding
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = response.data[0].embedding
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'score': 1 - results['distances'][0][i]  # Convert distance to similarity
            })
        
        return formatted_results
    
    def is_ready(self) -> bool:
        return self.ready
    
    def get_total_chunks(self) -> int:
        return self.collection.count()
    
    def get_last_updated(self) -> Optional[str]:
        return self.last_updated
# incremental_saas_embeddings.py - Enhanced Vector Store with Incremental Updates
from __future__ import annotations

import os
import time
import uuid
import hashlib
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Set

import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

def content_hash(text: str) -> str:
    """Generate SHA256 hash of content"""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def _now_iso() -> str:
    return datetime.now().isoformat()

def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if v is not None else default

class IncrementalMemcacheS3VectorStore:
    """Enhanced vector store with incremental updates and change detection"""

    def __init__(
        self,
        user_id: str,
        knowledge_base_id: str,
        model_name: str = "models/embedding-001",
    ):
        self.user_id = user_id
        self.knowledge_base_id = knowledge_base_id
        self.model_name = model_name

        # State
        self.chunks: List[Dict] = []
        self.ready: bool = False
        self.last_updated: Optional[str] = None
        self.batch_size: int = int(os.getenv("EMBED_BATCH", "32"))
        self.embedding_dim: Optional[int] = None

        # NEW: Content hash tracking
        self.url_hashes: Dict[str, str] = {}  # url -> content_hash
        self.doc_hashes: Dict[str, str] = {}  # doc_id -> content_hash

        # Configure Google APIs
        google_api_key = _env("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        genai.configure(api_key=google_api_key)

        # Collection naming
        self.collection_name = f"user_{user_id}_kb_{knowledge_base_id}".replace("-", "_")
        self.hashes_collection = f"{self.collection_name}_hashes"

        # Qdrant client
        self.client = self._setup_qdrant()
        self._load_existing_data()

    def _setup_qdrant(self) -> QdrantClient:
        """Initialize Qdrant client"""
        url = _env("QDRANT_URL", "http://localhost:6333")
        api_key = _env("QDRANT_API_KEY")

        if "qdrant:6333" in url:
            url = url.replace("qdrant:6333", "localhost:6333")

        client = QdrantClient(url=url, api_key=api_key, timeout=60)

        try:
            _ = client.get_collections()
            logger.info("✅ Connected to Qdrant at %s", url)
        except Exception as e:
            logger.error("❌ Failed to connect to Qdrant: %s", e)
            raise

        return client

    def _ensure_collection(self, vector_dim: int) -> None:
        """Create collection if missing"""
        try:
            existing = self.client.get_collections().collections
            names = {c.name for c in existing}
            
            if self.collection_name not in names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
                )
                logger.info("✅ Created collection '%s'", self.collection_name)

            # Create hashes collection for metadata
            if self.hashes_collection not in names:
                self.client.create_collection(
                    collection_name=self.hashes_collection,
                    vectors_config=VectorParams(size=1, distance=Distance.COSINE),  # Dummy vector
                )
                logger.info("✅ Created hashes collection '%s'", self.hashes_collection)

        except Exception as e:
            logger.error("Error ensuring collection: %s", e)
            raise

    def _load_existing_data(self) -> None:
        """Load existing data and hashes"""
        try:
            # Load content hashes
            self._load_content_hashes()
            
            # Check if main collection exists
            info = self.client.get_collection(self.collection_name)
            count = getattr(info, "points_count", None)
            if isinstance(count, int) and count > 0:
                self.ready = True
                self.last_updated = _now_iso()
                logger.info("✅ Found %d existing points", count)

        except Exception:
            logger.info("📭 No existing data found")

    def _load_content_hashes(self) -> None:
        """Load stored content hashes from Qdrant"""
        try:
            response = self.client.scroll(
                collection_name=self.hashes_collection,
                limit=1000,
                with_payload=True
            )
            
            for point in response[0]:
                payload = point.payload
                if payload.get("type") == "url_hash":
                    self.url_hashes[payload["url"]] = payload["hash"]
                elif payload.get("type") == "doc_hash":
                    self.doc_hashes[payload["doc_id"]] = payload["hash"]
                    
            logger.info("📦 Loaded %d URL hashes, %d doc hashes", 
                       len(self.url_hashes), len(self.doc_hashes))
        except Exception as e:
            logger.debug("Could not load hashes: %s", e)

    def _save_content_hash(self, identifier: str, hash_value: str, hash_type: str) -> None:
        """Save content hash to Qdrant"""
        try:
            self._ensure_collection(1)  # Ensure hashes collection exists
            
            point_id = f"{hash_type}_{content_hash(identifier)}"
            payload = {
                "type": hash_type,
                "hash": hash_value,
                "updated_at": _now_iso()
            }
            
            if hash_type == "url_hash":
                payload["url"] = identifier
            else:
                payload["doc_id"] = identifier

            point = PointStruct(
                id=point_id,
                vector=[0.0],  # Dummy vector
                payload=payload
            )
            
            self.client.upsert(collection_name=self.hashes_collection, points=[point])
            
        except Exception as e:
            logger.error("Error saving hash: %s", e)

    async def _generate_embeddings_google(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Google API"""
        logger.info("🔄 Processing %d texts with Google Embedding API", len(texts))

        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=8)

        def _embed(text: str) -> Optional[List[float]]:
            try:
                r = genai.embed_content(model=self.model_name, content=text, task_type="retrieval_document")
                emb = r["embedding"] if isinstance(r, dict) else getattr(r, "embedding", None)
                return emb
            except Exception as e:
                logger.error("Embedding error: %s", e)
                return None

        # Detect dimension
        if not self.embedding_dim:
            try:
                test = await loop.run_in_executor(executor, _embed, "dimension probe")
                if test:
                    self.embedding_dim = len(test)
            except Exception as e:
                logger.error("Failed to probe embedding dim: %s", e)

        futures = [loop.run_in_executor(executor, _embed, t) for t in texts]
        results = await asyncio.gather(*futures)

        dim = self.embedding_dim or 768
        fixed = [r if (r and isinstance(r, list) and len(r) == dim) else [0.0] * dim for r in results]

        return fixed

    def _create_chunks(self, page: Dict) -> List[Dict]:
        """Create chunks from page content"""
        try:
            content = page.get("content", "")
            if not content or len(content) < 100:
                return []

            max_chars = 1536  # ~512 tokens
            overlap = 80

            sentences = [s.strip() for s in content.split(".") if s.strip()]
            chunks = []
            cur = ""

            for s in sentences:
                s_dot = s + ". "
                if len(cur) + len(s_dot) > max_chars:
                    if cur:
                        chunks.append({
                            "text": cur.strip(),
                            "metadata": {
                                "source_url": page.get("url", ""),
                                "title": page.get("title", ""),
                                "chunk_index": len(chunks),
                                "scraped_at": page.get("scraped_at", _now_iso()),
                            },
                        })
                    cur_tail = cur[-overlap:] if len(cur) > overlap else cur
                    cur = (cur_tail + s_dot).strip()
                else:
                    cur += s_dot

            if cur.strip():
                chunks.append({
                    "text": cur.strip(),
                    "metadata": {
                        "source_url": page.get("url", ""),
                        "title": page.get("title", ""),
                        "chunk_index": len(chunks),
                        "scraped_at": page.get("scraped_at", _now_iso()),
                    },
                })

            return chunks
        except Exception as e:
            logger.error("Error creating chunks: %s", e)
            return []

    async def _remove_points_by_url(self, url: str) -> int:
        """Remove all points associated with a specific URL"""
        try:
            # Find points with this URL
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="source_url",
                        match=MatchValue(value=url)
                    )
                ]
            )
            
            response = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=1000,
                with_payload=False  # We only need IDs
            )
            
            point_ids = [point.id for point in response[0]]
            
            if point_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(points=point_ids)
                )
                logger.info("🗑️ Removed %d points for URL: %s", len(point_ids), url)
                return len(point_ids)
            
            return 0
            
        except Exception as e:
            logger.error("Error removing points for URL %s: %s", url, e)
            return 0

    async def process_pages_incremental(self, pages: List[Dict]) -> Dict[str, int]:
        """Process pages with incremental updates - only update changed content"""
        logger.info("🔄 Processing %d pages incrementally", len(pages))
        
        stats = {"updated": 0, "skipped": 0, "new": 0, "removed": 0}
        
        for page in pages:
            try:
                url = page.get("url", "")
                current_content = page.get("content", "")
                current_hash = content_hash(current_content)
                stored_hash = self.url_hashes.get(url)
                
                if current_hash == stored_hash:
                    # Content unchanged, skip
                    stats["skipped"] += 1
                    logger.debug("⏭️ Skipping unchanged: %s", url)
                    continue
                
                # Content changed or new
                if stored_hash:
                    # Remove old content
                    removed = await self._remove_points_by_url(url)
                    stats["removed"] += removed
                    stats["updated"] += 1
                    logger.info("🔄 Updating changed content: %s", url)
                else:
                    stats["new"] += 1
                    logger.info("➕ Adding new content: %s", url)
                
                # Add new content
                chunks = self._create_chunks(page)
                if chunks:
                    await self._add_chunks_to_qdrant(chunks)
                    
                    # Update hash tracking
                    self.url_hashes[url] = current_hash
                    self._save_content_hash(url, current_hash, "url_hash")
                
            except Exception as e:
                logger.error("Error processing page %s: %s", page.get("url", ""), e)
                continue
        
        # Update state
        self.ready = True
        self.last_updated = _now_iso()
        
        logger.info("✅ Incremental update complete: %s", stats)
        return stats

    async def _add_chunks_to_qdrant(self, chunks: List[Dict]) -> None:
        """Add chunks to Qdrant"""
        if not chunks:
            return
            
        texts = [c["text"] for c in chunks]
        embeddings = await self._generate_embeddings_google(texts)
        dim = self.embedding_dim or 768
        
        self._ensure_collection(dim)
        
        points = []
        for chunk, vec in zip(chunks, embeddings):
            payload = {
                "content": chunk["text"],
                "source_url": chunk["metadata"]["source_url"],
                "title": chunk["metadata"]["title"],
                "chunk_index": chunk["metadata"]["chunk_index"],
                "scraped_at": chunk["metadata"]["scraped_at"],
            }
            points.append(PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload))
        
        # Batch insert
        batch_size = max(128, self.batch_size)
        for i in range(0, len(points), batch_size):
            self.client.upsert(collection_name=self.collection_name, points=points[i:i + batch_size])

    # ENHANCED: Smart process_pages that detects if incremental update is possible
    async def process_pages(self, pages: List[Dict], clear_existing: bool = None) -> None:
        """Process pages - automatically choose incremental vs full update"""
        
        # Auto-detect: if we have existing data and hashes, use incremental
        if clear_existing is None:
            has_existing = self.ready and len(self.url_hashes) > 0
            clear_existing = not has_existing
        
        if clear_existing:
            logger.info("🚀 Full processing mode")
            self.clear_data(silent=True)
            
            # Standard full processing
            all_chunks = []
            for page in pages:
                try:
                    chunks = self._create_chunks(page)
                    all_chunks.extend(chunks)
                    
                    # Track hash for future incremental updates
                    url = page.get("url", "")
                    content_hash_val = content_hash(page.get("content", ""))
                    self.url_hashes[url] = content_hash_val
                    self._save_content_hash(url, content_hash_val, "url_hash")
                    
                except Exception as e:
                    logger.error("Chunking error: %s", e)
            
            if not all_chunks:
                logger.error("❌ No chunks created!")
                return
                
            # Generate embeddings and store
            texts = [c["text"] for c in all_chunks]
            embeddings = await self._generate_embeddings_google(texts)
            dim = self.embedding_dim or 768
            
            self._ensure_collection(dim)
            
            points = []
            for ch, vec in zip(all_chunks, embeddings):
                payload = {
                    "content": ch["text"],
                    "source_url": ch["metadata"]["source_url"],
                    "title": ch["metadata"]["title"],
                    "chunk_index": ch["metadata"]["chunk_index"],
                    "scraped_at": ch["metadata"]["scraped_at"],
                }
                points.append(PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload))
            
            # Bulk upload
            try:
                info = self.client.get_collection(self.collection_name)
                existing = int(getattr(info, "points_count", 0) or 0)
            except Exception:
                existing = 0
            
            if existing == 0 and len(points) > 0:
                self.client.upload_collection(
                    collection_name=self.collection_name,
                    vectors=[p.vector for p in points],
                    payload=[p.payload for p in points],
                    ids=[p.id for p in points],
                    batch_size=max(128, self.batch_size),
                )
            else:
                batch_size = max(128, self.batch_size)
                for i in range(0, len(points), batch_size):
                    self.client.upsert(collection_name=self.collection_name, points=points[i:i + batch_size])
            
            self.chunks = all_chunks
            logger.info("✅ Full processing complete: %d chunks", len(all_chunks))
            
        else:
            logger.info("🔄 Incremental processing mode")
            stats = await self.process_pages_incremental(pages)
            logger.info("✅ Incremental processing complete: %s", stats)
        
        self.ready = True
        self.last_updated = _now_iso()

    # Keep all existing methods unchanged
    async def process_document(self, document_data: dict) -> int:
        """Process a single document with incremental support"""
        try:
            text_content = document_data.get("text", "")
            metadata = document_data.get("metadata", {})
            if not text_content.strip():
                return 0

            # Generate document ID for tracking
            doc_id = metadata.get("source_url", f"doc_{uuid.uuid4()}")
            current_hash = content_hash(text_content)
            stored_hash = self.doc_hashes.get(doc_id)
            
            # Check if content changed
            if current_hash == stored_hash:
                logger.info("⏭️ Document unchanged, skipping: %s", metadata.get("title", doc_id))
                return 0

            # Remove old version if exists
            if stored_hash:
                await self._remove_points_by_url(doc_id)
                logger.info("🔄 Updating document: %s", metadata.get("title", doc_id))

            page = {
                "content": text_content,
                "url": doc_id,
                "title": metadata.get("title", "Uploaded Document"),
                "scraped_at": metadata.get("uploaded_at", _now_iso()),
            }

            chunks = self._create_chunks(page)
            if not chunks:
                return 0

            await self._add_chunks_to_qdrant(chunks)
            
            # Update hash tracking
            self.doc_hashes[doc_id] = current_hash
            self._save_content_hash(doc_id, current_hash, "doc_hash")

            self.chunks.extend(chunks)
            self.ready = True
            self.last_updated = _now_iso()

            logger.info("✅ Added %d chunks from document: %s", len(chunks), metadata.get("title", "Unknown"))
            return len(chunks)
            
        except Exception as e:
            logger.error("Error processing document: %s", e)
            return 0

    async def add_document(self, document_data: Dict) -> int:
        """Backward compatibility"""
        return await self.process_document(document_data)

    def clear_data(self, silent: bool = False) -> None:
        """Clear all data"""
        try:
            self.client.delete_collection(self.collection_name)
            self.client.delete_collection(self.hashes_collection)
            self.chunks = []
            self.url_hashes = {}
            self.doc_hashes = {}
            self.ready = False
            self.last_updated = None
            if not silent:
                logger.info("🗑️ Cleared all data for %s/%s", self.user_id, self.knowledge_base_id)
        except Exception as e:
            logger.error("Error clearing data: %s", e)

    async def semantic_search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Semantic search (unchanged)"""
        if not self.is_ready():
            return []
        try:
            qr = genai.embed_content(model=self.model_name, content=query, task_type="retrieval_query")
            qvec = qr["embedding"] if isinstance(qr, dict) else getattr(qr, "embedding", None)
            if not qvec:
                return []

            res = self.client.search(
                collection_name=self.collection_name,
                query_vector=qvec,
                limit=max_results,
                with_payload=True,
            )

            out = []
            for r in res:
                payload = r.payload or {}
                out.append({
                    "text": payload.get("content", ""),
                    "metadata": {
                        "source_url": payload.get("source_url", ""),
                        "title": payload.get("title", ""),
                        "chunk_index": payload.get("chunk_index", -1),
                        "scraped_at": payload.get("scraped_at", ""),
                    },
                    "score": float(getattr(r, "score", 0.0) or 0.0),
                })
            return out
        except Exception as e:
            logger.error("Error in semantic search: %s", e)
            return []

    async def process_query(self, question: str, max_results: int = 5) -> Dict:
        """Process query (unchanged)"""
        if not self.is_ready():
            return {"answer": "Knowledge base is not ready.", "sources": [], "confidence": 0.0}
        
        try:
            chunks = await self.semantic_search(question, max_results)
            if not chunks:
                return {"answer": "I couldn't find relevant information.", "sources": [], "confidence": 0.0}

            context = "\n\n".join([c["text"] for c in chunks])
            sources = [c["metadata"] for c in chunks]
            answer = await self._generate_answer_google(question, context)
            return {"answer": answer, "sources": sources, "confidence": 0.8}
        except Exception as e:
            logger.error("Error processing query: %s", e)
            return {"answer": "Sorry, I encountered an error.", "sources": [], "confidence": 0.0}

    async def _generate_answer_google(self, question: str, context: str) -> str:
        """Generate answer (unchanged)"""
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = (
                "You are a helpful sales assistant. Based on the following information, "
                "concisely answer the customer's question.\n\n"
                f"Information:\n{context}\n\n"
                f"Customer Question: {question}\n\n"
                "Answer:"
            )
            resp = model.generate_content(prompt)
            return getattr(resp, "text", None) or "I'll get back to you with that information."
        except Exception as e:
            logger.error("Error generating answer: %s", e)
            return "I'll get back to you with that information."

    def is_ready(self) -> bool:
        """Check if ready (unchanged)"""
        if not self.ready:
            try:
                info = self.client.get_collection(self.collection_name)
                count = int(getattr(info, "points_count", 0) or 0)
                if count > 0:
                    self.ready = True
            except Exception:
                return False
        return self.ready

    def get_total_chunks(self) -> int:
        """Get total chunks (unchanged)"""
        try:
            info = self.client.get_collection(self.collection_name)
            return int(getattr(info, "points_count", 0) or 0)
        except Exception:
            return len(self.chunks)

# Backward compatibility - replace the original class
MemcacheS3VectorStore = IncrementalMemcacheS3VectorStore
SaaSVectorStore = IncrementalMemcacheS3VectorStore
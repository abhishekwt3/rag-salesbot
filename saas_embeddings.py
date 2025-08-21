# saas_embeddings.py - Multi-tenant Vector Store with Google Embeddings + Qdrant + Incremental Updates
from __future__ import annotations

import os
import time
import uuid
import math
import hashlib
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional

# Google Embedding + Gemini API
import google.generativeai as genai

# Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

# Async helpers
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# -----------------------------
# Utility helpers
# -----------------------------

_DEF_MAX_WORKERS = int(os.getenv("EMBED_MAX_WORKERS", "8"))
_DEF_BATCH_SIZE = int(os.getenv("EMBED_BATCH", "32"))
_DEF_SEARCH_LIMIT = 5

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if v is not None else default

def content_hash(text: str) -> str:
    """Generate SHA256 hash of content for change detection"""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()

def _chunk_text(text: str, target_words: int = 220, overlap_words: int = 40) -> List[str]:
    """Word-based chunking with overlap for better context preservation"""
    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(1, target_words - overlap_words)
    for i in range(0, len(words), step):
        segment = words[i : i + target_words]
        if not segment:
            break
        chunks.append(" ".join(segment).strip())
        if i + target_words >= len(words):
            break
    return chunks

# -----------------------------
# Main Vector Store
# -----------------------------

class MemcacheS3VectorStore:
    """Multi-tenant vector store using Google Embeddings + Qdrant with efficient incremental updates."""

    def __init__(
        self,
        user_id: str,
        knowledge_base_id: str,
        model_name: str = "models/embedding-001",
    ):
        self.user_id = str(user_id)
        self.knowledge_base_id = str(knowledge_base_id)
        self.model_name = model_name

        # state
        self.ready: bool = False
        self.last_updated: Optional[str] = None
        self.batch_size: int = _DEF_BATCH_SIZE
        self.embedding_dim: Optional[int] = None

        # Configure Google APIs
        google_api_key = _env("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        genai.configure(api_key=google_api_key)

        # Single collection with tenant filtering (more scalable)
        self.collection_name = os.getenv("QDRANT_COLLECTION", "kb_chunks")

        # Qdrant client
        self.client = self._setup_qdrant()
        self._load_existing_data()

    def _setup_qdrant(self) -> QdrantClient:
        """Initialize Qdrant client"""
        url = _env("QDRANT_URL", "http://localhost:6333")
        api_key = _env("QDRANT_API_KEY")
        prefer_grpc = _env("QDRANT_GRPC", "false").lower() in {"1", "true", "yes"}

        if "qdrant:6333" in url:
            url = url.replace("qdrant:6333", "localhost:6333")

        client = QdrantClient(url=url, api_key=api_key, prefer_grpc=prefer_grpc, timeout=60)

        try:
            _ = client.get_collections()
            logger.info("✅ Connected to Qdrant at %s", url)
        except Exception as e:
            logger.error("❌ Failed to connect to Qdrant: %s", e)
            raise

        return client

    async def _ensure_collection(self):
        """Create collection if missing with proper dimension"""
        if self.embedding_dim is None:
            # Determine dimension by embedding a probe
            vec = await self._embed_text("dimension probe")
            if vec is None:
                raise RuntimeError("Embedding failed. Check GOOGLE_API_KEY.")
            self.embedding_dim = len(vec)

        try:
            existing = self.client.get_collections().collections
            names = {c.name for c in existing}
            
            if self.collection_name not in names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.embedding_dim, distance=Distance.COSINE),
                )
                logger.info("✅ Created collection '%s' (dim=%d)", self.collection_name, self.embedding_dim)
        except Exception as e:
            logger.error("Error ensuring collection: %s", e)
            raise

    def _load_existing_data(self) -> None:
        """Check if we have existing data"""
        try:
            count = self.get_total_chunks()
            if count > 0:
                self.ready = True
                self.last_updated = _now_iso()
                logger.info("✅ Found %d existing chunks", count)
        except Exception:
            logger.info("📭 No existing data found")

    def _point_id(self, source_id: str, chunk_index: int) -> str:
        """Generate deterministic UUID-format point ID for safe upserts"""
        base = f"{self.user_id}:{self.knowledge_base_id}:{source_id}:{chunk_index}"
        hash_hex = content_hash(base)
        
        # Convert first 32 chars of hash to UUID format
        # xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        uuid_str = f"{hash_hex[:8]}-{hash_hex[8:12]}-{hash_hex[12:16]}-{hash_hex[16:20]}-{hash_hex[20:32]}"
        return uuid_str

    def _tenant_filter(self, extra: Optional[List] = None) -> Filter:
        """Create filter for this tenant+KB"""
        conditions = [
            FieldCondition(key="tenant_id", match=MatchValue(value=self.user_id)),
            FieldCondition(key="kb_id", match=MatchValue(value=self.knowledge_base_id)),
        ]
        if extra:
            conditions.extend(extra)
        return Filter(must=conditions)

    def _get_existing_points_for_source(self, source_id: str) -> List:
        """Get all existing points for a source"""
        try:
            filter_condition = self._tenant_filter([
                FieldCondition(key="source_id", match=MatchValue(value=source_id))
            ])
            
            collected = []
            offset = None
            while True:
                response = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=filter_condition,
                    limit=256,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                points, offset = response
                collected.extend(points or [])
                if offset is None or not points:
                    break
            return collected
        except Exception as e:
            logger.warning("Error fetching existing points: %s", e)
            return []

    async def _generate_embeddings_google(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Google API with parallel processing"""
        if not texts:
            return []

        logger.info("🔄 Processing %d texts with Google Embedding API", len(texts))

        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=_DEF_MAX_WORKERS)

        def _embed(text: str) -> Optional[List[float]]:
            try:
                r = genai.embed_content(model=self.model_name, content=text, task_type="retrieval_document")
                emb = r["embedding"] if isinstance(r, dict) else getattr(r, "embedding", None)
                return emb
            except Exception as e:
                logger.error("Embedding error: %s", e)
                return None

        futures = [loop.run_in_executor(executor, _embed, t) for t in texts]
        results = await asyncio.gather(*futures)

        dim = self.embedding_dim or 768
        return [r if (r and isinstance(r, list) and len(r) == dim) else [0.0] * dim for r in results]

    async def _embed_text(self, text: str) -> Optional[List[float]]:
        """Embed single text"""
        if not text.strip():
            return None
        try:
            r = genai.embed_content(model=self.model_name, content=text, task_type="retrieval_document")
            return r["embedding"] if isinstance(r, dict) else getattr(r, "embedding", None)
        except Exception as e:
            logger.error("Embedding error: %s", e)
            return None

    async def _process_single_source(self, text: str, source_id: str, extra_meta: Dict) -> int:
        """Process single source with incremental updates"""
        text = (text or "").strip()
        if not text:
            return 0

        # Create chunks
        chunks = _chunk_text(text)
        if not chunks:
            return 0

        # Get existing points for this source
        existing_points = self._get_existing_points_for_source(source_id)
        existing_by_index = {p.payload.get("chunk_index"): p for p in existing_points}

        # Prepare new/changed chunks
        points_to_upsert = []
        upsert_count = 0

        for idx, chunk in enumerate(chunks):
            chunk_hash = content_hash(chunk)
            point_id = self._point_id(source_id, idx)
            
            # Check if chunk changed
            existing_point = existing_by_index.get(idx)
            existing_hash = existing_point.payload.get("chunk_hash") if existing_point else None
            
            if existing_hash == chunk_hash:
                continue  # Unchanged, skip
            
            # Embed new/changed chunk
            vec = await self._embed_text(chunk)
            if vec is None:
                continue

            payload = {
                "tenant_id": self.user_id,
                "kb_id": self.knowledge_base_id,
                "source_id": source_id,
                "text": chunk,
                "chunk_index": idx,
                "chunk_hash": chunk_hash,
                "updated_at": _now_iso(),
                **extra_meta
            }

            points_to_upsert.append(PointStruct(
                id=point_id,
                vector=vec,
                payload=payload
            ))
            upsert_count += 1

        # Upsert changed/new chunks
        if points_to_upsert:
            batch_size = max(128, self.batch_size)
            for i in range(0, len(points_to_upsert), batch_size):
                batch = points_to_upsert[i:i + batch_size]
                self.client.upsert(collection_name=self.collection_name, points=batch, wait=True)

        # Delete removed chunks
        new_indices = set(range(len(chunks)))
        points_to_delete = []
        for idx, point in existing_by_index.items():
            if idx not in new_indices:
                points_to_delete.append(point.id)

        if points_to_delete:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=points_to_delete,
                wait=True
            )

        return upsert_count

    # -----------------------------
    # Public API
    # -----------------------------

    async def process_pages(self, pages: List[Dict], clear_existing: bool = False) -> None:
        """Process multiple pages with incremental updates"""
        logger.info("🚀 Processing %d pages with incremental updates", len(pages))
        start = time.time()

        await self._ensure_collection()

        if clear_existing:
            self.clear_data(silent=True)

        total_upserts = 0
        for page in pages:
            try:
                url = page.get("final_url") or page.get("url") or ""
                content = page.get("text") or page.get("content") or ""
                title = page.get("title") or ""
                
                if not url or not content.strip():
                    continue

                extra_meta = {
                    "url": url,
                    "title": title,
                    "source_type": "web",
                    "framework": page.get("framework", "unknown"),
                    "word_count": page.get("word_count", 0),
                    "scraped_at": page.get("scraped_at", _now_iso()),
                }

                upserts = await self._process_single_source(content, url, extra_meta)
                total_upserts += upserts

            except Exception as e:
                logger.error("Error processing page %s: %s", page.get("url", ""), e)

        self.ready = True
        self.last_updated = _now_iso()
        
        logger.info("✅ Processed %d pages, %d chunks upserted in %.2fs", 
                   len(pages), total_upserts, time.time() - start)

    async def process_document(self, document_data: dict) -> int:
        """Process single document with incremental updates"""
        try:
            await self._ensure_collection()
            
            text_content = document_data.get("text", "")
            metadata = document_data.get("metadata", {})
            
            if not text_content.strip():
                return 0

            source_id = metadata.get("source_url") or metadata.get("doc_id") or f"doc_{uuid.uuid4()}"
            
            extra_meta = {
                "source_type": "document",
                "title": metadata.get("title", "Uploaded Document"),
                "file_type": metadata.get("file_type", ""),
                **metadata
            }

            upserts = await self._process_single_source(text_content, source_id, extra_meta)
            
            self.ready = True
            self.last_updated = _now_iso()

            logger.info("Added %d chunks from document: %s", upserts, extra_meta.get("title"))
            return upserts

        except Exception as e:
            logger.error("Error processing document: %s", e)
            return 0

    async def add_document(self, document_data: Dict) -> int:
        """Backward compatibility"""
        return await self.process_document(document_data)

    async def semantic_search(self, query: str, max_results: int = _DEF_SEARCH_LIMIT) -> List[Dict]:
        """Semantic search with tenant filtering"""
        if not self.is_ready():
            return []
        
        try:
            qvec = await self._embed_text(query)
            if not qvec:
                return []

            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=qvec,
                limit=max_results,
                query_filter=self._tenant_filter(),
                with_payload=True,
            )

            output = []
            for r in results:
                payload = r.payload or {}
                output.append({
                    "text": payload.get("text", ""),
                    "metadata": {
                        "source_url": payload.get("url", ""),
                        "title": payload.get("title", ""),
                        "chunk_index": payload.get("chunk_index", -1),
                        "scraped_at": payload.get("scraped_at", ""),
                    },
                    "score": float(getattr(r, "score", 0.0) or 0.0),
                })
            return output

        except Exception as e:
            logger.error("Search error: %s", e)
            return []

    async def process_query(self, question: str, max_results: int = _DEF_SEARCH_LIMIT) -> Dict:
        """Process query with search and answer generation"""
        if not self.is_ready():
            return {
                "answer": "Knowledge base is not ready. Please process some content first.",
                "sources": [],
                "confidence": 0.0,
            }

        try:
            chunks = await self.semantic_search(question, max_results)
            if not chunks:
                return {
                    "answer": "I couldn't find relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0
                }

            context = "\n\n".join([c["text"] for c in chunks])
            sources = [c["metadata"] for c in chunks]
            answer = await self._generate_answer_google(question, context)
            
            # Simple confidence from top score
            confidence = chunks[0]["score"] if chunks else 0.0
            
            return {"answer": answer, "sources": sources, "confidence": confidence}

        except Exception as e:
            logger.error("Query processing error: %s", e)
            return {
                "answer": "Sorry, I encountered an error processing your question.",
                "sources": [],
                "confidence": 0.0
            }

    async def _generate_answer_google(self, question: str, context: str) -> str:
        """Generate answer using Google Gemini"""
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = (
                "You are a helpful sales assistant. Based on the following information, "
                "concisely answer the customer's question and focus on how our features can help them.\n\n"
                f"Information:\n{context}\n\n"
                f"Customer Question: {question}\n\n"
                "Answer as a knowledgeable sales assistant. If you don't have the specific information needed, say you'll get back to them."
            )
            resp = model.generate_content(prompt)
            return getattr(resp, "text", None) or "I'll get back to you with that information."
        except Exception as e:
            logger.error("Answer generation error: %s", e)
            return "I'll get back to you with that information."

    def is_ready(self) -> bool:
        """Check if vector store is ready"""
        if not self.ready:
            try:
                count = self.get_total_chunks()
                if count > 0:
                    self.ready = True
            except Exception:
                return False
        return self.ready

    def get_total_chunks(self) -> int:
        """Get total chunks for this tenant+KB"""
        try:
            result = self.client.count(
                collection_name=self.collection_name,
                count_filter=self._tenant_filter(),
            )
            return int(result.count) if hasattr(result, "count") else 0
        except Exception as e:
            logger.warning("Count failed: %s", e)
            return 0

    def clear_data(self, silent: bool = False) -> None:
        """Delete all data for this tenant+KB"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=self._tenant_filter(),
                wait=True,
            )
            self.ready = False
            self.last_updated = None
            if not silent:
                logger.info("🗑️ Cleared all data for %s/%s", self.user_id, self.knowledge_base_id)
        except Exception as e:
            if not silent:
                logger.error("Error clearing data: %s", e)

# Backward compatibility alias
SaaSVectorStore = MemcacheS3VectorStore
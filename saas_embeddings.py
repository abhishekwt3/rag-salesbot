# saas_embeddings.py - Multi-tenant Vector Store with Google Embeddings + Qdrant (rewritten)

from __future__ import annotations

import os
import time
import uuid
import math
import logging
from datetime import datetime
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
    return datetime.now().isoformat()


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if v is not None else default


# -----------------------------
# Main Vector Store
# -----------------------------

class MemcacheS3VectorStore:
    """Multi-tenant vector store using Google Embeddings + Qdrant (rewritten).

    Public API preserved from the user's original file.
    """

    def __init__(
        self,
        user_id: str,
        knowledge_base_id: str,
        model_name: str = "models/embedding-001",
    ):
        self.user_id = user_id
        self.knowledge_base_id = knowledge_base_id
        self.model_name = model_name

        # state
        self.chunks: List[Dict] = []
        self.ready: bool = False
        self.last_updated: Optional[str] = None
        self.batch_size: int = _DEF_BATCH_SIZE
        self.embedding_dim: Optional[int] = None  # determined after first embed

        # Configure Google APIs
        google_api_key = _env("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        genai.configure(api_key=google_api_key)

        # Collection naming (underscored to be safe)
        self.collection_name = (
            f"user_{user_id}_kb_{knowledge_base_id}".replace("-", "_")
        )

        # Qdrant client
        self.client = self._setup_qdrant()

        # Try to read existing state (points_count, vector size if possible)
        self._load_existing_data()

    # -----------------------------
    # Qdrant setup & schema
    # -----------------------------

    def _setup_qdrant(self) -> QdrantClient:
        """Initialize Qdrant client with sensible defaults."""
        url = _env("QDRANT_URL", "http://localhost:6333")
        api_key = _env("QDRANT_API_KEY")
        prefer_grpc = _env("QDRANT_GRPC", "false").lower() in {"1", "true", "yes"}

        # Handle Docker service name resolution for local development
        if "qdrant:6333" in url:
            url = url.replace("qdrant:6333", "localhost:6333")
            logger.info("Adjusted Qdrant URL for local development: %s", url)

        client = QdrantClient(
            url=url,
            api_key=api_key,
            prefer_grpc=prefer_grpc,
            timeout=60,
        )

        # Health check
        try:
            _ = client.get_collections()
            logger.info("✅ Connected to Qdrant at %s (grpc=%s)", url, prefer_grpc)
        except Exception as e:
            logger.error("❌ Failed to connect to Qdrant at %s: %s", url, e)
            raise

        return client

    def _ensure_collection(self, vector_dim: int) -> None:
        """Create collection if missing; ensure vector size matches, else recreate."""
        try:
            existing = self.client.get_collections().collections
            names = {c.name for c in existing}
            if self.collection_name not in names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
                )
                logger.info("✅ Created Qdrant collection '%s' (dim=%d)", self.collection_name, vector_dim)
                return

            # validate vector size
            info = self.client.get_collection(self.collection_name)
            current_dim = info.vectors_count and info.config.params.vectors.size if hasattr(info, "config") else None
            if current_dim and int(current_dim) != int(vector_dim):
                logger.warning(
                    "⚠️ Collection dim mismatch (have=%s, need=%s). Recreating '%s'...",
                    current_dim,
                    vector_dim,
                    self.collection_name,
                )
                self.client.delete_collection(self.collection_name)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE),
                )
                logger.info("✅ Recreated collection '%s' with dim=%d", self.collection_name, vector_dim)
        except Exception as e:
            logger.error("Error ensuring collection: %s", e)
            raise

    def _load_existing_data(self) -> None:
        """Best-effort load of existing collection info."""
        try:
            info = self.client.get_collection(self.collection_name)
        except Exception:
            logger.info("📭 No existing data found")
            return

        # points_count
        count = getattr(info, "points_count", None)
        if isinstance(count, int) and count > 0:
            self.ready = True
            self.last_updated = _now_iso()
            logger.info("✅ Found %d existing points in Qdrant", count)

        # try to infer dim
        try:
            # info.config.params.vectors.size for recent clients
            cfg = getattr(info, "config", None)
            if cfg and getattr(cfg, "params", None) and getattr(cfg.params, "vectors", None):
                self.embedding_dim = int(cfg.params.vectors.size)
        except Exception:
            pass

    # -----------------------------
    # Embeddings
    # -----------------------------

    async def _generate_embeddings_google(self, texts: List[str], concurrency: int = _DEF_MAX_WORKERS) -> List[List[float]]:
        """Parallel embedding using Google Embedding API.
        Returns embeddings in the **same order** as input.
        """
        logger.info("🔄 Processing %d texts with Google Embedding API (parallel)", len(texts))

        loop = asyncio.get_event_loop()
        executor = ThreadPoolExecutor(max_workers=concurrency)

        def _embed(text: str, task_type: str) -> Optional[List[float]]:
            try:
                r = genai.embed_content(model=self.model_name, content=text, task_type=task_type)
                emb = r["embedding"] if isinstance(r, dict) else getattr(r, "embedding", None)
                return emb
            except Exception as e:
                logger.error("Embedding error: %s", e)
                return None

        # Detect dimension with a quick call (document type)
        if not self.embedding_dim:
            try:
                test = await loop.run_in_executor(executor, _embed, "dimension probe", "retrieval_document")
                if test:
                    self.embedding_dim = len(test)
                    logger.info("📏 Detected embedding dimension: %d", self.embedding_dim)
            except Exception as e:
                logger.error("Failed to probe embedding dim: %s", e)

        # Submit all jobs as retrieval_document
        futures = [loop.run_in_executor(executor, _embed, t, "retrieval_document") for t in texts]
        results: List[Optional[List[float]]] = await asyncio.gather(*futures)

        dim = self.embedding_dim or 768
        # Replace failures with zero vectors of correct size
        fixed = [r if (r and isinstance(r, list) and len(r) == dim) else [0.0] * dim for r in results]

        return fixed

    # -----------------------------
    # Chunking
    # -----------------------------

    def _create_chunks(self, page: Dict) -> List[Dict]:
        """Token-aware-ish chunking using char proxy (3 chars ≈ 1 token).
        Adds slight overlap to preserve context.
        """
        try:
            content = page.get("content", "")
            if not content or len(content) < 100:
                return []

            max_tokens = 512
            max_chars = max_tokens * 3
            overlap = 80

            sentences = [s.strip() for s in content.split(".") if s.strip()]
            chunks: List[Dict] = []
            cur = ""

            for s in sentences:
                s_dot = s + ". "
                if len(cur) + len(s_dot) > max_chars:
                    if cur:
                        chunks.append(
                            {
                                "text": cur.strip(),
                                "metadata": {
                                    "source_url": page.get("url", ""),
                                    "title": page.get("title", ""),
                                    "chunk_index": len(chunks),
                                    "scraped_at": page.get("scraped_at", _now_iso()),
                                },
                            }
                        )
                    cur_tail = cur[-overlap:] if len(cur) > overlap else cur
                    cur = (cur_tail + s_dot).strip()
                else:
                    cur += s_dot

            if cur.strip():
                chunks.append(
                    {
                        "text": cur.strip(),
                        "metadata": {
                            "source_url": page.get("url", ""),
                            "title": page.get("title", ""),
                            "chunk_index": len(chunks),
                            "scraped_at": page.get("scraped_at", _now_iso()),
                        },
                    }
                )

            return chunks
        except Exception as e:
            logger.error("Error creating chunks: %s", e)
            return []

    # -----------------------------
    # Ingestion
    # -----------------------------

    async def process_pages(self, pages: List[Dict], clear_existing: bool = True) -> None:
        """Process multiple pages (scraped website pages)."""
        logger.info("🚀 Processing %d pages with Google + Qdrant...", len(pages))
        start = time.time()

        if clear_existing:
            self.clear_data(silent=True)

        # Build chunks
        all_chunks: List[Dict] = []
        for page in pages:
            try:
                all_chunks.extend(self._create_chunks(page))
            except Exception as e:
                logger.error("Chunking error: %s", e)
        if not all_chunks:
            logger.error("❌ No chunks created!")
            return
        logger.info("✅ Created %d chunks", len(all_chunks))

        # Embed (detect dimension)
        texts = [c["text"] for c in all_chunks]
        embeddings = await self._generate_embeddings_google(texts)
        dim = self.embedding_dim or 768

        # Ensure collection exists w/ correct dim
        self._ensure_collection(dim)

        # Prepare points
        points: List[PointStruct] = []
        for ch, vec in zip(all_chunks, embeddings):
            payload = {
                "content": ch["text"],  # keep full; Qdrant payloads can handle it
                "source_url": ch["metadata"]["source_url"],
                "title": ch["metadata"]["title"],
                "chunk_index": ch["metadata"]["chunk_index"],
                "scraped_at": ch["metadata"]["scraped_at"],
            }
            points.append(PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload))

        # Upload efficiently: if collection empty, upload_collection (fast path), else upsert in batches
        try:
            info = self.client.get_collection(self.collection_name)
            existing = int(getattr(info, "points_count", 0) or 0)
        except Exception:
            existing = 0

        try:
            if existing == 0 and len(points) > 0:
                # One-shot bulk upload
                self.client.upload_collection(
                    collection_name=self.collection_name,
                    vectors=[p.vector for p in points],
                    payload=[p.payload for p in points],
                    ids=[p.id for p in points],
                    batch_size=max(128, self.batch_size),
                )
            else:
                # Upsert in batches
                bs = max(128, self.batch_size)
                for i in range(0, len(points), bs):
                    self.client.upsert(collection_name=self.collection_name, points=points[i : i + bs])
            logger.info("✅ Stored %d points in Qdrant", len(points))
        except Exception as e:
            logger.error("❌ Qdrant insert failed: %s", e)

        # Update state and verify
        self.chunks = all_chunks
        self.ready = True
        self.last_updated = _now_iso()

        stored = self.get_total_chunks()
        logger.info("✅ Verified %s chunks stored in Qdrant", stored)
        logger.info("🎉 Processed %d chunks in %.2fs", len(all_chunks), time.time() - start)

    async def process_document(self, document_data: dict) -> int:
        """Process a single document payload {text, metadata} and add to the vector store."""
        try:
            text_content = document_data.get("text", "")
            metadata = document_data.get("metadata", {})
            if not text_content.strip():
                return 0

            page = {
                "content": text_content,
                "url": metadata.get("source_url", "uploaded_file"),
                "title": metadata.get("title", "Uploaded Document"),
                "scraped_at": metadata.get("uploaded_at", _now_iso()),
            }

            chunks = self._create_chunks(page)
            if not chunks:
                return 0

            texts = [c["text"] for c in chunks]
            embeddings = await self._generate_embeddings_google(texts)
            dim = self.embedding_dim or 768
            self._ensure_collection(dim)

            points: List[PointStruct] = []
            for ch, vec in zip(chunks, embeddings):
                payload = {
                    "content": ch["text"],
                    "source_url": ch["metadata"]["source_url"],
                    "title": ch["metadata"]["title"],
                    "chunk_index": ch["metadata"]["chunk_index"],
                    "scraped_at": ch["metadata"]["scraped_at"],
                }
                points.append(PointStruct(id=str(uuid.uuid4()), vector=vec, payload=payload))

            # Upsert in reasonable batch
            bs = max(128, self.batch_size)
            for i in range(0, len(points), bs):
                self.client.upsert(collection_name=self.collection_name, points=points[i : i + bs])

            self.chunks.extend(chunks)
            self.ready = True
            self.last_updated = _now_iso()

            logger.info("Added %d chunks from document: %s", len(chunks), metadata.get("title", "Unknown"))
            return len(chunks)
        except Exception as e:
            logger.error("Error processing document: %s", e)
            return 0

    async def add_document(self, document_data: Dict) -> int:
        """Backward-compat shim; delegates to process_document."""
        return await self.process_document(document_data)

    def clear_data(self, silent: bool = False) -> None:
        """Delete collection content and recreate lazily when next ingest runs."""
        try:
            self.client.delete_collection(self.collection_name)
            # Do not recreate here; we will create with correct dim after embeddings
            self.chunks = []
            self.ready = False
            self.last_updated = None
            if not silent:
                logger.info("🗑️ Cleared all data for %s/%s", self.user_id, self.knowledge_base_id)
        except Exception as e:
            logger.error("Error clearing data: %s", e)

    # -----------------------------
    # Search & QA
    # -----------------------------

    async def semantic_search(self, query: str, max_results: int = _DEF_SEARCH_LIMIT) -> List[Dict]:
        if not self.is_ready():
            return []
        try:
            # Query embedding
            qr = genai.embed_content(model=self.model_name, content=query, task_type="retrieval_query")
            qvec = qr["embedding"] if isinstance(qr, dict) else getattr(qr, "embedding", None)
            if not qvec:
                return []

            res = self.client.search(
                collection_name=self.collection_name,
                query_vector=qvec,
                limit=max_results,
                with_payload=True,
                score_threshold=None,
            )

            out: List[Dict] = []
            for r in res:
                payload = r.payload or {}
                out.append(
                    {
                        "text": payload.get("content", ""),
                        "metadata": {
                            "source_url": payload.get("source_url", ""),
                            "title": payload.get("title", ""),
                            "chunk_index": payload.get("chunk_index", -1),
                            "scraped_at": payload.get("scraped_at", ""),
                        },
                        "score": float(getattr(r, "score", 0.0) or 0.0),
                    }
                )
            return out
        except Exception as e:
            logger.error("Error in semantic search: %s", e)
            return []

    async def process_query(self, question: str, max_results: int = _DEF_SEARCH_LIMIT) -> Dict:
        if not self.is_ready():
            return {
                "answer": "Knowledge base is not ready. Please process some content first.",
                "sources": [],
                "confidence": 0.0,
            }
        try:
            chunks = await self.semantic_search(question, max_results)
            if not chunks:
                return {"answer": "I couldn't find relevant information to answer your question.", "sources": [], "confidence": 0.0}

            context = "\n\n".join([c["text"] for c in chunks])
            sources = [c["metadata"] for c in chunks]
            answer = await self._generate_answer_google(question, context)
            return {"answer": answer, "sources": sources, "confidence": 0.8}
        except Exception as e:
            logger.error("Error processing query: %s", e)
            return {"answer": "Sorry, I encountered an error processing your question.", "sources": [], "confidence": 0.0}

    async def _generate_answer_google(self, question: str, context: str) -> str:
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            prompt = (
                "You are a helpful sales assistant. Based on the following information, concisely answer the customer's question and focus on how our features can help them.\n\n"
                f"Information:\n{context}\n\n"
                f"Customer Question: {question}\n\n"
                "Answer as a knowledgeable sales assistant. If you don't have the specific information needed, say you'll get back to them."
            )
            resp = model.generate_content(prompt)
            return getattr(resp, "text", None) or "I'll get back to you with that information. Please try again."
        except Exception as e:
            logger.error("Error generating answer with Google API: %s", e)
            return "I'll get back to you with that information. Please try again."

    # -----------------------------
    # State helpers
    # -----------------------------

    def is_ready(self) -> bool:
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
        try:
            info = self.client.get_collection(self.collection_name)
            return int(getattr(info, "points_count", 0) or 0)
        except Exception:
            return len(self.chunks)

    def __del__(self):
        try:
            if hasattr(self, "client") and self.client:
                self.client.close()
        except Exception:
            pass


# Backward compatibility alias
SaaSVectorStore = MemcacheS3VectorStore
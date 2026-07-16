"""
AI Retrieval — RAG document retrieval and reranking.

Retrieves semantically relevant documents from OpenSearch
using dense embeddings and optional reranking for precision.

Exports:
  DocumentRetriever  — Main RAG retrieval pipeline (embed → search → rerank).
  Reranker           — Cross-encoder reranker for improving retrieval precision.
  RetrievedDocument  — Dataclass for a single retrieved document chunk.
"""

"""Embedding providers.

This keeps the dependency injection simple for the rest of the system.
In a real build, this is where you'd plug in OpenAI embeddings or a
HuggingFace model based on config.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import List


@dataclass
class EmbeddingsConfig:
    provider: str = os.getenv("EMBEDDINGS_PROVIDER", "openai")
    openai_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    hf_model: str = os.getenv("HF_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def _safe_import_openai():
    try:
        import openai  # type: ignore

        return openai
    except Exception:  # pragma: no cover
        return None


def _safe_import_sentence_transformers():
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore

        return SentenceTransformer
    except Exception:  # pragma: no cover
        return None


class Embeddings:
    def __init__(self, cfg: EmbeddingsConfig) -> None:
        self.cfg = cfg

    def embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        provider = self.cfg.provider.lower()
        if provider == "openai":
            return self._embed_openai(texts)
        return self._embed_hf(texts)

    def _embed_openai(self, texts: List[str]) -> List[List[float]]:
        # A pragmatic placeholder: this lets the scaffolding run without an API key.
        openai = _safe_import_openai()
        if openai is None:
            return self._embed_stub(texts)

        client = openai.OpenAI()  # expects env OPENAI_API_KEY
        resp = client.embeddings.create(model=self.cfg.openai_model, input=texts)
        return [d.embedding for d in resp.data]

    def _embed_hf(self, texts: List[str]) -> List[List[float]]:
        SentenceTransformer = _safe_import_sentence_transformers()
        if SentenceTransformer is None:
            return self._embed_stub(texts)

        model = SentenceTransformer(self.cfg.hf_model)
        vectors = model.encode(texts, normalize_embeddings=True)
        return vectors.tolist()

    @staticmethod
    def _embed_stub(texts: List[str]) -> List[List[float]]:
        # This is intentionally dumb: it's mainly here to prevent hard failures
        # when you just want the repo to install and boot.
        return [[float(len(t))] for t in texts]


@lru_cache(maxsize=1)
def get_embeddings() -> Embeddings:
    return Embeddings(EmbeddingsConfig())

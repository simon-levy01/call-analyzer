from __future__ import annotations

import json
import threading
from functools import lru_cache
from pathlib import Path
from typing import Sequence

import numpy as np


MODEL_NAME = "BAAI/bge-small-en-v1.5"
MODEL_DIMENSION = 384
_MARKER = "semantic-ready-v1.json"
_EMBED_LOCK = threading.Lock()


def default_cache_dir(database_path: Path) -> Path:
    return database_path.parent / "models" / "bge-small-en-v1.5"


def model_ready(cache_dir: Path) -> bool:
    return embed_texts_if_ready(["offline readiness check"], cache_dir) is not None


@lru_cache(maxsize=2)
def _offline_model(cache_dir: str):
    from fastembed import TextEmbedding

    return TextEmbedding(
        model_name=MODEL_NAME,
        cache_dir=cache_dir,
        threads=2,
        local_files_only=True,
    )


def embed_texts_if_ready(texts: Sequence[str], cache_dir: Path) -> np.ndarray | None:
    if not texts or not (cache_dir / _MARKER).is_file():
        return None
    try:
        with _EMBED_LOCK:
            vectors = np.asarray(
                list(_offline_model(str(cache_dir)).embed(list(texts))), dtype=np.float32
            )
    except Exception:
        return None
    if vectors.shape != (len(texts), MODEL_DIMENSION) or not np.all(np.isfinite(vectors)):
        return None
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    if np.any(norms == 0) or not np.all(np.isfinite(norms)):
        return None
    return vectors / norms


def install_model(cache_dir: Path) -> dict[str, int | str]:
    from fastembed import TextEmbedding

    cache_dir.mkdir(parents=True, exist_ok=True)
    model = TextEmbedding(model_name=MODEL_NAME, cache_dir=str(cache_dir), threads=2)
    vector = np.asarray(next(iter(model.embed(["offline readiness check"]))), dtype=np.float32)
    if vector.shape != (MODEL_DIMENSION,):
        raise RuntimeError("semantic model returned an unexpected vector size")
    _offline_model.cache_clear()
    offline_vector = np.asarray(
        next(iter(_offline_model(str(cache_dir)).embed(["offline readiness check"]))),
        dtype=np.float32,
    )
    if offline_vector.shape != (MODEL_DIMENSION,):
        raise RuntimeError("semantic model did not pass its offline startup check")
    (cache_dir / _MARKER).write_text(
        json.dumps({"model": MODEL_NAME, "dimension": MODEL_DIMENSION}),
        encoding="utf-8",
    )
    size = sum(path.stat().st_size for path in cache_dir.rglob("*") if path.is_file())
    return {"model": MODEL_NAME, "dimension": MODEL_DIMENSION, "cache_bytes": size}

# embeddings.py

import os
import numpy as np
from langchain_ollama import OllamaEmbeddings

# --------------------------------
# Ollama config (local / tunnel)
# --------------------------------
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://localhost:11434"
)

embeddings = OllamaEmbeddings(
    model="mxbai-embed-large:latest",
    base_url=OLLAMA_BASE_URL
)

# --------------------------------
# Embed text
# --------------------------------
def embed_text(text: str) -> list:
    if not text or not text.strip():
        return []

    return embeddings.embed_query(text.strip())


# --------------------------------
# Cosine similarity (safe)
# --------------------------------
def cosine_similarity(a, b) -> float:
    if not a or not b:
        return 0.0

    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)

    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0

    return float(np.dot(a, b) / denom)

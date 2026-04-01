import numpy as np
from volcenginesdkarkruntime import Ark

from ..config import BASE_URL, API_KEY, EMBEDDING_MODEL
from ..llm import get_embedding_client


def get_text_embedding(text: str) -> list[float]:
    client = get_embedding_client()
    resp = client.multimodal_embeddings.create(
        model=EMBEDDING_MODEL,
        input=[{"type": "text", "text": text}],
        encoding_format="float",
    )
    return resp.data.embedding


def get_text_embeddings(texts: list[str]) -> list[list[float]]:
    client = get_embedding_client()
    embeddings = []
    for text in texts:
        resp = client.multimodal_embeddings.create(
            model=EMBEDDING_MODEL,
            input=[{"type": "text", "text": text}],
            encoding_format="float",
        )
        embeddings.append(resp.data.embedding)
    return embeddings


def cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr = np.array(a)
    b_arr = np.array(b)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))

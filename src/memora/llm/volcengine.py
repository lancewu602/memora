import os
from volcenginesdkarkruntime import Ark

from ..config import BASE_URL, API_KEY, LLM_MODEL


def get_ark_client() -> Ark:
    return Ark(
        base_url=BASE_URL,
        api_key=API_KEY or os.environ.get("ARK_API_KEY", ""),
    )


def get_embedding_client() -> Ark:
    return get_ark_client()


def get_llm_client() -> Ark:
    return get_ark_client()

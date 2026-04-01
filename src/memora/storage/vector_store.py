import chromadb
from chromadb.config import Settings

from ..config import CHROMA_PATH, MEMORY_COLLECTION
from ..embeddings import get_text_embedding


client = chromadb.PersistentClient(path=str(CHROMA_PATH), settings=Settings(anonymized_telemetry=False))


def get_collection():
    return client.get_or_create_collection(MEMORY_COLLECTION)


def store_memory(memory_id: str, content: str, metadata: dict = None):
    collection = get_collection()
    embedding = get_text_embedding(content)
    meta = metadata or {}
    meta["content"] = content
    collection.add(
        documents=[content],
        ids=[memory_id],
        embeddings=[embedding],
        metadatas=[meta],
    )


def search_memories(query: str, n_results: int = 10) -> list[dict]:
    collection = get_collection()
    query_embedding = get_text_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )
    memories = []
    if results["ids"] and len(results["ids"]) > 0:
        for i, memory_id in enumerate(results["ids"][0]):
            memories.append({
                "id": memory_id,
                "content": results["documents"][0][i] if results["documents"] else "",
                "distance": results["distances"][0][i] if results["distances"] else None,
                "metadata": results["metadatas"][0][i] if results["metadatas"] else None,
            })
    return memories


def get_memory(memory_id: str) -> dict:
    collection = get_collection()
    result = collection.get(ids=[memory_id])
    if result["ids"]:
        return {
            "id": result["ids"][0],
            "content": result["documents"][0] if result["documents"] else "",
            "metadata": result["metadatas"][0] if result["metadatas"] else None,
        }
    return None


def update_memory(memory_id: str, content: str, metadata: dict = None):
    collection = get_collection()
    embedding = get_text_embedding(content)
    meta = metadata or {}
    meta["content"] = content
    collection.update(
        ids=[memory_id],
        documents=[content],
        embeddings=[embedding],
        metadatas=[meta],
    )


def delete_memory(memory_id: str):
    collection = get_collection()
    collection.delete(ids=[memory_id])

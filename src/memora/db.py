import chromadb
from chromadb.config import Settings
from pathlib import Path

DB_PATH = Path.home() / ".memora" / "chromadb"

client = chromadb.PersistentClient(path=str(DB_PATH), settings=Settings(anonymized_telemetry=False))


def get_collection(name: str, metadata: dict = None):
    return client.get_or_create_collection(name, metadata=metadata)


def add_documents(collection_name: str, documents: list, ids: list, metadata: list = None):
    collection = get_collection(collection_name)
    collection.add(documents=documents, ids=ids, metadata=metadata)


def query_documents(collection_name: str, query_texts: list, n_results: int = 10, where: dict = None):
    collection = get_collection(collection_name)
    return collection.query(query_texts=query_texts, n_results=n_results, where=where)


def get_document(collection_name: str, id: str):
    collection = get_collection(collection_name)
    return collection.get(ids=[id])


def delete_document(collection_name: str, id: str):
    collection = get_collection(collection_name)
    collection.delete(ids=[id])


def update_document(collection_name: str, id: str, documents: str = None, metadata: dict = None):
    collection = get_collection(collection_name)
    collection.update(ids=[id], documents=[documents] if documents else None, metadata=[metadata] if metadata else None)


def list_collections():
    return client.list_collections()



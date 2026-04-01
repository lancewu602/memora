import json
import uuid
from typing import Optional

from ..llm import get_llm_client
from ..config import LLM_MODEL
from ..storage import (
    store_memory as store_to_vector,
    search_memories,
    add_memory as add_to_sqlite,
    get_memory as get_from_sqlite,
    update_memory as update_in_sqlite,
    delete_memory as delete_from_sqlite,
    get_memory,
    update_memory as update_vector,
    delete_memory as delete_from_vector,
)
from .prompts import INTENT_CLASSIFICATION_PROMPT


def store_memory(content: str, tags: Optional[str] = None) -> dict:
    memory_id = str(uuid.uuid4())
    metadata = {"tags": tags} if tags else None
    try:
        store_to_vector(memory_id, content, metadata)
        add_to_sqlite(memory_id, content, tags)
        return {
            "success": True,
            "memory_id": memory_id,
            "message": "记忆已成功存储"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "存储记忆失败"
        }


def search_memory(query: str, n_results: int = 5) -> dict:
    try:
        results = search_memories(query, n_results)
        if not results:
            return {
                "success": True,
                "results": [],
                "message": "没有找到相关记忆"
            }
        return {
            "success": True,
            "results": results,
            "message": f"找到 {len(results)} 条相关记忆"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "搜索记忆失败"
        }


def update_memory(memory_id: str, new_content: str, tags: Optional[str] = None) -> dict:
    existing = get_memory(memory_id)
    if not existing:
        return {
            "success": False,
            "error": "记忆不存在",
            "message": "要修改的记忆不存在"
        }
    try:
        metadata = {"tags": tags} if tags else None
        update_vector(memory_id, new_content, metadata)
        update_in_sqlite(memory_id, new_content, tags)
        return {
            "success": True,
            "memory_id": memory_id,
            "message": "记忆已成功更新"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "更新记忆失败"
        }


def delete_memory(memory_id: str) -> dict:
    existing = get_memory(memory_id)
    if not existing:
        return {
            "success": False,
            "error": "记忆不存在",
            "message": "要删除的记忆不存在"
        }
    try:
        delete_from_vector(memory_id)
        delete_from_sqlite(memory_id)
        return {
            "success": True,
            "memory_id": memory_id,
            "message": "记忆已成功删除"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "删除记忆失败"
        }


def classify_intent(user_input: str) -> str:
    client = get_llm_client()
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "user", "content": INTENT_CLASSIFICATION_PROMPT.format(user_input=user_input)}
            ],
        )
        intent = response.choices[0].message.content.strip().lower()
        if intent in ["store", "search", "update", "delete"]:
            return intent
        return "search"
    except Exception:
        return "search"

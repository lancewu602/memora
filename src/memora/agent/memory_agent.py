import json
from typing import TypedDict

from langgraph.graph import StateGraph, END

from ..llm import get_llm_client
from ..config import LLM_MODEL
from .tools import (
    store_memory,
    search_memory,
    update_memory,
    delete_memory,
    classify_intent,
)
from .prompts import SYSTEM_PROMPT


class AgentState(TypedDict):
    user_input: str
    intent: str
    memory_content: str
    memory_id: str
    query: str
    new_content: str
    tags: str
    result: dict
    response: str


def parse_store_request(user_input: str, client) -> dict:
    prompt = f"""请分析用户想要存储的记忆内容，并提取标签（如果有）。

用户输入：{user_input}

请返回JSON格式：
{{"content": "记忆内容", "tags": "标签1,标签2" 或 null}}
"""
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return json.loads(content.strip())
    except Exception:
        return {"content": user_input, "tags": None}


def parse_search_request(user_input: str, client) -> str:
    return user_input


def parse_update_request(user_input: str, client) -> dict:
    prompt = f"""请分析用户想要修改记忆的内容。

用户输入：{user_input}

请返回JSON格式：
{{"memory_id": "从输入中提取的记忆ID，如果用户没有提供则返回null", "new_content": "新的记忆内容"}}
"""
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return json.loads(content.strip())
    except Exception:
        return {"memory_id": None, "new_content": user_input}


def parse_delete_request(user_input: str, client) -> str:
    prompt = f"""请从用户输入中提取要删除的记忆ID。

用户输入：{user_input}

请只返回记忆ID，如果用户没有提供ID，请根据上下文推断或返回null。
"""
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return None


def should_store(state: AgentState) -> bool:
    return state["intent"] == "store"


def should_search(state: AgentState) -> bool:
    return state["intent"] == "search"


def should_update(state: AgentState) -> bool:
    return state["intent"] == "update"


def should_delete(state: AgentState) -> bool:
    return state["intent"] == "delete"


def store_node(state: AgentState) -> AgentState:
    client = get_llm_client()
    parsed = parse_store_request(state["user_input"], client)
    result = store_memory(parsed["content"], parsed.get("tags"))
    state["result"] = result
    if result["success"]:
        state["response"] = f"已成功存储记忆，记忆ID：{result['memory_id']}"
    else:
        state["response"] = f"存储记忆失败：{result.get('message', '未知错误')}"
    return state


def search_node(state: AgentState) -> AgentState:
    query = state.get("query") or state["user_input"]
    result = search_memory(query)
    state["result"] = result
    if result["success"]:
        if result["results"]:
            response_text = f"找到 {len(result['results'])} 条相关记忆：\n"
            for i, mem in enumerate(result["results"], 1):
                response_text += f"\n{i}. {mem['content']}"
                if mem.get("metadata", {}).get("tags"):
                    response_text += f" (标签: {mem['metadata']['tags']})"
            state["response"] = response_text
        else:
            state["response"] = "没有找到相关记忆"
    else:
        state["response"] = f"搜索失败：{result.get('message', '未知错误')}"
    return state


def update_node(state: AgentState) -> AgentState:
    client = get_llm_client()
    parsed = parse_update_request(state["user_input"], client)
    memory_id = parsed.get("memory_id")
    if not memory_id:
        state["response"] = "无法确定要修改的记忆ID，请提供具体的记忆ID"
        state["result"] = {"success": False, "error": "memory_id not found"}
        return state
    result = update_memory(memory_id, parsed["new_content"])
    state["result"] = result
    if result["success"]:
        state["response"] = f"已成功更新记忆"
    else:
        state["response"] = f"更新记忆失败：{result.get('message', '未知错误')}"
    return state


def delete_node(state: AgentState) -> AgentState:
    client = get_llm_client()
    memory_id = parse_delete_request(state["user_input"], client)
    if not memory_id or memory_id == "null":
        state["response"] = "无法确定要删除的记忆ID，请提供具体的记忆ID"
        state["result"] = {"success": False, "error": "memory_id not found"}
        return state
    result = delete_memory(memory_id)
    state["result"] = result
    if result["success"]:
        state["response"] = f"已成功删除记忆"
    else:
        state["response"] = f"删除记忆失败：{result.get('message', '未知错误')}"
    return state


def intent_node(state: AgentState) -> AgentState:
    intent = classify_intent(state["user_input"])
    state["intent"] = intent
    return state


def build_agent() -> StateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("intent", intent_node)
    graph.add_node("store", store_node)
    graph.add_node("search", search_node)
    graph.add_node("update", update_node)
    graph.add_node("delete", delete_node)

    graph.set_entry_point("intent")

    graph.add_conditional_edges(
        "intent",
        lambda state: state["intent"],
        {
            "store": "store",
            "search": "search",
            "update": "update",
            "delete": "delete",
        }
    )

    graph.add_edge("store", END)
    graph.add_edge("search", END)
    graph.add_edge("update", END)
    graph.add_edge("delete", END)

    return graph.compile()


agent = build_agent()


def run_agent(user_input: str) -> str:
    initial_state: AgentState = {
        "user_input": user_input,
        "intent": "",
        "memory_content": "",
        "memory_id": "",
        "query": "",
        "new_content": "",
        "tags": "",
        "result": {},
        "response": "",
    }
    final_state = agent.invoke(initial_state)
    return final_state.get("response", "处理失败")

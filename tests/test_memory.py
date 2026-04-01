import os
import sys
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

os.environ["ARK_API_KEY"] = "test-api-key"
os.environ["ARK_BASE_URL"] = "ark.cn-beijing.volces.com/api/v3"
os.environ["LLM_MODEL"] = "doubao-seed-2-0-lite-260215"
os.environ["EMBEDDING_MODEL"] = "doubao-embedding-vision-251215"

from memora.storage.sqlite_db import (
    add_memory,
    get_memory,
    update_memory,
    delete_memory,
    list_memories,
)
from memora.agent.tools import store_memory, search_memory, update_memory, delete_memory


class TestSQLiteDB:
    def setup_method(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        import memora.storage.sqlite_db as db_module
        db_module.SQLITE_PATH = self.temp_db.name
        from memora.storage.sqlite_db import init_db
        init_db()

    def teardown_method(self):
        os.unlink(self.temp_db.name)

    def test_add_and_get_memory(self):
        success = add_memory("test-id-1", "今天天气真好", "天气,心情")
        assert success is True
        memory = get_memory("test-id-1")
        assert memory is not None
        assert memory["content"] == "今天天气真好"
        assert memory["tags"] == "天气,心情"

    def test_get_nonexistent_memory(self):
        memory = get_memory("nonexistent-id")
        assert memory is None

    def test_update_memory(self):
        add_memory("test-id-2", "原始内容", "标签1")
        result = update_memory("test-id-2", "更新后的内容", "新标签")
        assert result["success"] is True
        memory = get_memory("test-id-2")
        assert memory["content"] == "更新后的内容"
        assert memory["tags"] == "新标签"

    def test_delete_memory(self):
        add_memory("test-id-3", "要被删除的记忆")
        result = delete_memory("test-id-3")
        assert result["success"] is True
        memory = get_memory("test-id-3")
        assert memory is None

    def test_list_memories(self):
        add_memory("test-id-4", "记忆1")
        add_memory("test-id-5", "记忆2")
        memories = list_memories()
        assert len(memories) >= 2


class TestAgentTools:
    @patch("memora.storage.vector_store.get_text_embedding")
    @patch("memora.storage.vector_store.client")
    def test_store_memory(self, mock_client, mock_embedding):
        mock_embedding.return_value = [0.1] * 3072
        mock_collection = MagicMock()
        mock_client.get_or_create_collection.return_value = mock_collection

        import memora.storage.vector_store as vs_module
        vs_module.client = mock_client

        result = store_memory("这是一条测试记忆", "测试")

        assert result["success"] is True
        assert "memory_id" in result

    @patch("memora.storage.vector_store.get_text_embedding")
    @patch("memora.storage.vector_store.client")
    def test_search_memory(self, mock_client, mock_embedding):
        mock_embedding.return_value = [0.1] * 3072
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "ids": [["test-id-1"]],
            "documents": [["测试记忆内容"]],
            "distances": [[0.1]],
            "metadatas": [[{"tags": "测试"}]],
        }
        mock_client.get_or_create_collection.return_value = mock_collection

        import memora.storage.vector_store as vs_module
        vs_module.client = mock_client

        result = search_memory("测试查询")

        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["results"][0]["content"] == "测试记忆内容"

    @patch("memora.agent.tools.get_memory")
    def test_update_memory_not_found(self, mock_get_memory):
        mock_get_memory.return_value = None
        result = update_memory("nonexistent-id", "新内容")
        assert result["success"] is False
        assert "不存在" in result["message"]

    @patch("memora.agent.tools.get_memory")
    def test_delete_memory_not_found(self, mock_get_memory):
        mock_get_memory.return_value = None
        result = delete_memory("nonexistent-id")
        assert result["success"] is False
        assert "不存在" in result["message"]


class TestTokenAuth:
    def test_generate_and_verify_token(self):
        from memora.auth import generate_token, verify_token
        token = generate_token("test-api-key")
        assert token is not None
        assert len(token.split(".")) == 3
        assert verify_token(token) is True

    def test_verify_invalid_token(self):
        from memora.auth import verify_token
        assert verify_token("invalid.token.here") is False
        assert verify_token("") is False

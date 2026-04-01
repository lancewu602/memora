import os
import sys
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

os.environ["ARK_API_KEY"] = "test-api-key"
os.environ["ARK_BASE_URL"] = "ark.cn-beijing.volces.com/api/v3"
os.environ["LLM_MODEL"] = "doubao-seed-2-0-lite-260215"
os.environ["EMBEDDING_MODEL"] = "doubao-embedding-vision-251215"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


class TestAPI:
    @patch("memora.api.run_agent")
    def test_chat_with_auth(self, mock_run_agent):
        mock_run_agent.return_value = "测试回复"
        from memora.api import app, generate_token
        token = generate_token("test-key-123")
        client = TestClient(app)
        response = client.post(
            "/api/v1/memory/chat",
            json={"message": "测试消息"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["response"] == "测试回复"

    def test_chat_empty_message(self):
        from memora.api import app, generate_token
        token = generate_token("test-key-123")
        client = TestClient(app)
        response = client.post(
            "/api/v1/memory/chat",
            json={"message": ""},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 400

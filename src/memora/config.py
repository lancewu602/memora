import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("ARK_BASE_URL", "ark.cn-beijing.volces.com/api/v3")
API_KEY = os.getenv("ARK_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "doubao-seed-2-0-lite-260215")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "doubao-embedding-vision-251215")

MEMORY_COLLECTION = "memories"

DB_PATH = Path.home() / ".memora"
DB_PATH.mkdir(parents=True, exist_ok=True)

CHROMA_PATH = DB_PATH / "chromadb"
SQLITE_PATH = DB_PATH / "memora.db"

TOKEN_SECRET = os.getenv("TOKEN_SECRET", "memora-secret-key-change-in-production")
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "720"))

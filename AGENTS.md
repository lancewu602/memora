# AGENTS.md - Memora Development Guide

This file provides guidance for agentic coding assistants working in this repository.

## Project Overview

Memora is a private memory agent assistant that provides RESTful APIs for mobile clients to save and search memories using natural language. It uses LangGraph as the Agent framework, Volcano Engine (ARK API) for LLM and embeddings, ChromaDB for vector storage, and SQLite for metadata.

## Build/Lint/Test Commands

### Poetry Commands
```bash
# Install dependencies
poetry install

# Update lock file
poetry lock

# Add a dependency
poetry add <package>
poetry add --group dev <package>

# Run scripts defined in pyproject.toml
poetry run <command>
```

### Testing
```bash
# Run all tests
poetry run pytest tests/ -v

# Run a single test file
poetry run pytest tests/test_memory.py -v

# Run a single test class
poetry run pytest tests/test_memory.py::TestSQLiteDB -v

# Run a single test
poetry run pytest tests/test_memory.py::TestSQLiteDB::test_add_and_get_memory -v
```

### Running the Application
```bash
# Run via module
poetry run python -m memora.main

# Or directly
poetry run memora
```

## Code Style Guidelines

### Python Version
- Requires Python >= 3.12

### Project Structure
```
src/memora/
├── __init__.py           # Package exports
├── config.py             # Configuration and environment variables
├── main.py               # Application entry point
├── api.py                # FastAPI routes
├── agent/                # LangGraph agent implementation
│   ├── memory_agent.py   # Agent graph and nodes
│   ├── tools.py          # Agent tools (store/search/update/delete)
│   └── prompts.py        # Prompt templates
├── embeddings/           # Embedding utilities
│   └── volcengine.py     # Volcano Engine embedding client
├── llm/                  # LLM client
│   └── volcengine.py     # Volcano Engine LLM client
├── storage/              # Data storage
│   ├── sqlite_db.py      # SQLite metadata operations
│   └── vector_store.py   # ChromaDB vector operations
└── auth/                 # Authentication
    └── token.py          # Token generation and verification
```

### Import Conventions
- Use absolute imports from package root: `from memora.storage import ...`
- Group imports: stdlib → third-party → local
- Use `__all__` to define public API in `__init__.py`

### Type Annotations
- Use type hints for all function parameters and return values
- Use `TypedDict` for complex state types (e.g., `AgentState`)
- Use `Optional[T]` instead of `T | None` for compatibility

### Naming Conventions
- **Modules**: snake_case (`vector_store.py`)
- **Classes**: PascalCase (`class MemoryAgent`)
- **Functions/methods**: snake_case (`def store_memory`)
- **Constants**: SCREAMING_SNAKE_CASE (`MAX_RESULTS`)
- **Variables**: snake_case (`memory_id`, `user_input`)

### Error Handling
- Return dict with `success`, `error`, `message` keys instead of raising exceptions in tools
- Use try/except with specific exception types
- Log errors appropriately
- API endpoints should return proper HTTP status codes (400 for bad request, 401 for auth failure, 500 for internal errors)

### FastAPI Guidelines
- Use Pydantic `BaseModel` for request/response schemas
- Use `Depends()` for dependency injection (e.g., auth)
- Use `asynccontextmanager` lifespan instead of deprecated `@app.on_event`
- Group endpoints by resource using prefixes (`/api/v1/`)

### Agent Design (LangGraph)
- Define `AgentState` as `TypedDict`
- Use `StateGraph` with explicit nodes
- Use conditional edges for intent routing
- Return `AgentState` from each node

### API Response Format
```python
# Success response
{"success": True, "memory_id": "...", "message": "..."}

# Error response
{"success": False, "error": "...", "message": "..."}

# API endpoint response
{"response": "..."}  # For chat endpoint
```

### Configuration
- Use `python-dotenv` for environment variables
- Define defaults in `config.py`
- Environment variables: `ARK_API_KEY`, `ARK_BASE_URL`, `LLM_MODEL`, `EMBEDDING_MODEL`, `TOKEN_SECRET`, `TOKEN_EXPIRE_HOOURS`

### Testing Guidelines
- Mock external services (LLM, embeddings) in unit tests
- Use `unittest.mock.patch` for mocking
- Test each layer independently: SQLite, vector store, agent tools, API
- Use in-memory SQLite (`:memory:`) or temporary files for test isolation

### Security
- Never commit secrets to version control
- Use environment variables for API keys
- Hash tokens before storage
- Use `hmac.compare_digest` for signature verification to prevent timing attacks

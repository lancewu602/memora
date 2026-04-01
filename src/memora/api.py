from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional

from .auth import generate_token, verify_token
from .storage import init_db, add_api_key
from .agent import run_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Memora - 私人记忆助手", lifespan=lifespan)


class TokenRequest(BaseModel):
    api_key: str


class TokenResponse(BaseModel):
    token: str
    token_type: str = "bearer"


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/v1/auth/token", response_model=TokenResponse)
async def get_token(request: TokenRequest):
    if not request.api_key:
        raise HTTPException(status_code=400, detail="API key is required")
    add_api_key(request.api_key)
    token = generate_token(request.api_key)
    return TokenResponse(token=token)


async def verify_auth_header(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    token = parts[1]
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token


@app.post("/api/v1/memory/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, token: str = Depends(verify_auth_header)):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
    try:
        response = run_agent(request.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

# app.py  (WITH CORS – IONIC READY)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.chat_service import handle_message
from db import chat_history_col

app = FastAPI(title="Clinic AI", version="1.0")

# -----------------------------
# CORS CONFIG (IONIC / ANGULAR)
# -----------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8100",   # Ionic dev
        "http://localhost:4200",   # Angular (optional)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Schemas
# -----------------------------

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    intent: str
    reply: str


# -----------------------------
# Chat Endpoint
# -----------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = handle_message(
        session_id=req.session_id,
        user_input=req.message
    )

    return ChatResponse(
        session_id=req.session_id,
        intent=result["intent"],
        reply=result["reply"]
    )


# -----------------------------
# Chat History (Left Panel)
# -----------------------------

@app.get("/chat/history/{session_id}")
def chat_history(session_id: str):
    history = list(
        chat_history_col.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1)
    )

    return {
        "session_id": session_id,
        "messages": history
    }


# -----------------------------
# Session List (Left Panel)
# -----------------------------

@app.get("/chat/sessions")
def chat_sessions():
    sessions = chat_history_col.distinct("session_id")
    return {"sessions": sessions}


# -----------------------------
# Health Check
# -----------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

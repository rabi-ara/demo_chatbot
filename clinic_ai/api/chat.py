from fastapi import APIRouter
from models import ChatRequest, ChatResponse
from services.chat_service import handle_message

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("")
def chat(req: ChatRequest):
    return handle_message(req.session_id, req.message)

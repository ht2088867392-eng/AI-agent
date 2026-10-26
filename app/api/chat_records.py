import logging

from fastapi import APIRouter, HTTPException, Request, status

from app.chat.schemas import ChatRequest, ChatResponse
from app.chat.service import ChatService

logger = logging.getLogger(__name__)

chat_router = APIRouter(
    prefix="/api/v1/chat",
    tags=["chat"],
)


@chat_router.post(
    "/messages",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
async def send_chat_message(
    payload: ChatRequest,
    request: Request,
) -> ChatResponse:
    agent = getattr(request.app.state, "agent", None)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="聊天服务尚未准备好",
        )

    try:
        conversation_id, reply = await ChatService(agent).send_message(
            conversation_id=payload.conversation_id,
            message=payload.message,
        )
    except Exception as exc:
        logger.exception("聊天请求处理失败")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="无法生成回复",
        ) from exc

    return ChatResponse(conversation_id=conversation_id, reply=reply)

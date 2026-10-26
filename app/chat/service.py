from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4


class ChatService:
    """封装调用 LangGraph 聊天 Agent 的应用服务。"""

    def __init__(self, agent: Any) -> None:
        self.agent = agent

    async def send_message(
        self,
        *,
        conversation_id: UUID | None,
        message: str,
    ) -> tuple[UUID, str]:
        conversation_id = conversation_id or uuid4()
        result = await self.agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]},
            config={
                "configurable": {
                    "thread_id": str(conversation_id),
                },
            },
        )

        messages = result.get("messages", [])
        if not messages:
            raise RuntimeError("Agent 未返回消息")

        reply = _message_content(messages[-1])
        if not reply:
            raise RuntimeError("Agent 返回了空响应")

        return conversation_id, reply


def _message_content(message: Any) -> str:
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "".join(parts)
    return str(content) if content is not None else ""

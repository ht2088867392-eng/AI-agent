import asyncio
from uuid import UUID

import pytest

from app.chat.schemas import ChatRequest
from app.chat.service import ChatService


class FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class FakeAgent:
    def __init__(self) -> None:
        self.calls = []

    async def ainvoke(self, input_value, *, config):
        self.calls.append((input_value, config))
        return {"messages": [FakeMessage("test reply")]}


def test_chat_service_assigns_separate_thread_ids():
    agent = FakeAgent()
    service = ChatService(agent)

    first_id, first_reply = asyncio.run(
        service.send_message(conversation_id=None, message="hello")
    )
    second_id, second_reply = asyncio.run(
        service.send_message(conversation_id=None, message="hello again")
    )

    assert first_id != second_id
    assert isinstance(first_id, UUID)
    assert first_reply == second_reply == "test reply"
    assert agent.calls[0][1]["configurable"]["thread_id"] == str(first_id)
    assert agent.calls[1][1]["configurable"]["thread_id"] == str(second_id)


def test_chat_service_reuses_existing_conversation_id():
    agent = FakeAgent()
    service = ChatService(agent)
    conversation_id = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")

    returned_id, _ = asyncio.run(
        service.send_message(
            conversation_id=conversation_id,
            message="continue",
        )
    )

    assert returned_id == conversation_id
    assert agent.calls[0][1]["configurable"]["thread_id"] == str(conversation_id)


def test_chat_request_rejects_blank_message_and_invalid_conversation_id():
    with pytest.raises(ValueError):
        ChatRequest(message="   ")

    with pytest.raises(ValueError):
        ChatRequest(conversation_id="not-a-uuid", message="hello")


def test_chat_request_strips_message_whitespace():
    request = ChatRequest(message="  hello  ")

    assert request.message == "hello"

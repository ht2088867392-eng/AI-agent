from typing import Literal
from pydantic import BaseModel, Field


class UserMemory(BaseModel):
    memory_type: Literal[
        "profile",
        "preference",
        "project",
        "instruction",
    ] = Field(description="长期记忆类型")

    content: str = Field(
        description="用户信息"
    )


class MemoryExtractionResult(BaseModel):
    memories: list[UserMemory]

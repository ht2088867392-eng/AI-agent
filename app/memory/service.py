import uuid
from langgraph.store.postgres import AsyncPostgresStore
from .schema import UserMemory


class MemoryService:

    def __init__(self, store: AsyncPostgresStore):
        self.store = store

    async def search(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
    ):
        return await self.store.asearch(
            ("memories", user_id),
            query=query,
            limit=limit,
        )

    async def save(
        self,
        user_id: str,
        memory: UserMemory,
    ):
        memory_id = str(uuid.uuid4())

        await self.store.aput(
            ("memories", user_id),
            memory_id,
            {
                "text": memory.content,
                "memory_type": memory.memory_type,
            },
        )

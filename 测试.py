import asyncio
from langgraph.store.postgres import AsyncPostgresStore
from app.config import Config
from langchain_openai import OpenAIEmbeddings

DB_URI = Config.DB_URI

embedding = OpenAIEmbeddings(
    model="BAAI/bge-large-zh-v1.5",
    api_key=Config.SILICONFLOW_API_KEY,
    base_url="https://api.siliconflow.cn/v1",
    check_embedding_ctx_length=False,
)


async def get_user_memories(
    store: AsyncPostgresStore,
    user_id: str,
    query: str,
):
    memories = await store.asearch(
        ("memories", user_id),
        query=query,
        limit=5,
    )

    return [
        item.value["text"]
        for item in memories
    ]


async def main():
    async with AsyncPostgresStore.from_conn_string(
            DB_URI,
            index={
                "dims": 1024,
                "embed": embedding,
                "fields": ["text"],
            },
    ) as store:

        # 精确读取
        results = await store.asearch(
            ("memories", "user_001"),
            query="用户做后端开发使用什么？",
            limit=5,
        )

        for item in results:
            print(item.value)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )
    asyncio.run(main())

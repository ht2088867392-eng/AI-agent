from app.agent.agent import get_agent, memory_store, config
import asyncio
from app.db.main import async_engine
import traceback
from app.memory.service import MemoryService
from app.memory.extractor import extract_memories

config = config


async def run(agent, store) -> None:
    print("个人视频助手已启动。")
    print("输入 exit 或 quit 退出。")
    memory_service = MemoryService(store)
    while True:
        try:
            user_input = input("\n你：").strip()

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit"}:
                print("已退出。")
                break

            # 读取长期记忆
            user_id = "user_001"
            memories = await memory_service.search(
                user_id=user_id,
                query=user_input,
            )
            memory_text = "\n".join(
                m.value["text"]
                for m in memories
            )
            messages = [
                {
                    "role": "system",
                    "content": memory_text
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ]

            # 调用agent
            result = await agent.ainvoke(
                {
                    "messages": messages
                },
                config=config
            )
            final_message = result["messages"][-1].content
            print(f"\nAI：{final_message}")

            # 写入长期记忆
            extracted_memories = await extract_memories(
                user_message=user_input,

            )
            for memory in extracted_memories:
                await memory_service.save(
                    user_id=user_id,
                    memory=memory,
                )

        except KeyboardInterrupt:
            print("\n已退出。")
            break

        except Exception as exc:
            print("异常类型：", type(exc).__name__)
            print("异常内容：", repr(exc))
            traceback.print_exc()


async def main() -> None:
    try:
        async with memory_store() as store:
            async with get_agent() as agent:
                await run(agent, store)
    finally:
        await async_engine.dispose()  # 释放数据库连接池


# 入口
if __name__ == "__main__":
    asyncio.set_event_loop_policy(
        asyncio.WindowsSelectorEventLoopPolicy()
    )

    asyncio.run(main())

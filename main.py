from app.agent.agent import agent
import asyncio
from app.db.main import async_engine
async def run() -> None:
    print("个人视频助手已启动。")
    print("输入 exit 或 quit 退出。")

    while True:
        try:
            user_input = input("\n你：").strip()

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit"}:
                print("已退出。")
                break

            result = await agent.ainvoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_input,
                        }
                    ]
                }
            )
            final_message = result["messages"][-1]
            print(f"\nAI：{final_message.content}")

        except KeyboardInterrupt:
            print("\n已退出。")
            break

        except Exception as exc:
            print(f"\n运行失败：{exc}")

async def main() -> None:
    try:
        await run()
    finally:
        await async_engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())



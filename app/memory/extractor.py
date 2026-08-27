from .schema import UserMemory,MemoryExtractionResult
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()
llm = init_chat_model(
    model="deepseek-chat",
    model_provider="deepseek",
)

memory_llm = llm.with_structured_output(
    MemoryExtractionResult
)


async def extract_memories(
    user_message: str,

) -> list[UserMemory]:

    result = await memory_llm.ainvoke(
        [
            {
                "role": "system",
                "content": """
你是长期记忆提取器。

你的任务是从用户与 AI 的本轮对话中，
提取未来聊天中仍然可能有价值的信息。

可以保存：
- 用户稳定身份、职业、背景
- 用户明确偏好
- 用户长期项目或技术栈
- 用户要求 AI 长期遵循的习惯

不要保存：
- 临时问题
- 一次性任务
- AI 自己推测的信息
- 普通知识
- 无长期价值的聊天内容

只记录用户明确表达或可靠确定的信息。

如果没有值得记住的信息，返回空 memories。
"""
            },
            {
                "role": "user",
                "content": f"""
用户：
{user_message}


"""
            },
        ]
    )

    return result.memories


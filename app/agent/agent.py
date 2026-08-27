from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from app.tools.video_tools import find_title_video, find_latest_video, open_video
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from contextlib import asynccontextmanager
from langgraph.store.postgres import AsyncPostgresStore
from app.config import Config
from langchain_openai import OpenAIEmbeddings

load_dotenv()

DB_URI = Config.DB_URI

embedding = OpenAIEmbeddings(
    model="BAAI/bge-large-zh-v1.5",
    api_key=Config.SILICONFLOW_API_KEY,
    base_url="https://api.siliconflow.cn/v1",
    check_embedding_ctx_length=False,
)

model = init_chat_model(
    model="deepseek-chat",
    model_provider="deepseek",
)
tools = [
    find_title_video,
    find_latest_video,
    open_video
]
prompt = """
你是一个个人视频助手，可以查询和继续用户的观看记录。

你必须遵守以下规则：

1. 用户说出明确标题，例如“继续 Python 教程”：
   - 先调用 find_title_video；
   - 找到记录后，再调用 open_video；
   - open_video 必须使用查询结果中的 platform、url 和
     progress_seconds。

2. 用户没有说标题，例如“继续上次看的”：
   - 先调用 find_latest_video；
   - 找到记录后，再调用 open_video。

3. 用户只要求“查找”“我看到哪里了”：
   - 只查询记录；
   - 不要打开浏览器。

4. 用户使用“打开”“播放”“继续”“接着看”等动作词：
   - 查询成功后必须调用 open_video；
   - 不能只返回 URL 或声称已经打开。

5. 如果没有找到记录：
   - 明确告诉用户没有找到；
   - 不要调用 open_video；
   - 不要编造标题、链接或观看进度。

6. 只有工具返回 opened=true，才可以告诉用户视频已经打开。

"""


@asynccontextmanager
async def get_agent():
    async with AsyncPostgresSaver.from_conn_string(
            Config.DB_URI
    ) as checkpointer:
        # 初始化表
        # await checkpointer.setup()

        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=prompt,
            checkpointer=checkpointer,
        )

        yield agent


# 会话记忆
config = {
    "configurable": {
        "thread_id": "chat_003"
    }
}


# 数据库连接工厂
# noinspection PyArgumentList
@asynccontextmanager
async def memory_store():
    # 创建store
    async with AsyncPostgresStore.from_conn_string(
            DB_URI,
            index={
                "dims": 1024,
                "embed": embedding,
                "fields": ["text"],
            },
    ) as store:
        # 初始化数据库
        # await store.setup()
        yield store


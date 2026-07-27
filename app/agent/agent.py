from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from app.tools.find_last_video import find_last_video


load_dotenv()

model = init_chat_model(
    model="deepseek-chat"
)

prompt="""
你是一个个人视频助手。
你的任务：
1.
理解用户想找的视频。
2.
调用工具查询观看记录。
3.
返回真实存在的视频信息。
不要编造记录。
"""


agent = create_agent(
    model=model,
    tools=[find_last_video],
    system_prompt=prompt
)


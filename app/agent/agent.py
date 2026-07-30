from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
from app.tools.video_tools import find_title_video,find_latest_video,open_video



load_dotenv()

model = init_chat_model(
    model="deepseek-chat"
)
tools = [
    find_title_video,
    find_latest_video,
    open_video
]
prompt="""
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


agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=prompt
)


from langchain.tools import tool

from app.db.database import search_video


@tool
def find_last_video(name: str) -> str:
    """
    查询用户最近观看的视频。

    输入:
    视频名称

    返回:
    视频地址和进度
    """

    result = search_video(name)

    if not result:
        return "没有找到观看记录"

    title, platform, url, position = result

    return f"""

视频:
{title}

平台:
{platform}

地址:
{url}

进度:
{position}

"""

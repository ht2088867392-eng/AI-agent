import webbrowser
from langchain.tools import tool
from app.video.service import VideoService,build_resume_url
from app.db.main import AsyncSessionLocal



video_service = VideoService()
@tool
async def find_title_video(name: str) -> dict:
    """
    按视频标题查询用户最近观看的一条记录。

    当用户提到明确的视频、课程或番剧名称时使用。
    """
    async with AsyncSessionLocal() as session:
        record = await video_service.find_title_video(name, session)

        if record is None:
            return {
                "found": False,
                "message": f"没有找到与“{name}”相关的观看记录。",
            }
        return {
            "found": True,
            "record_id": record.id,
            "title": record.title,
            "platform": record.platform,
            "url": record.url,
            "position_text": record.position_text,
            "progress_seconds": record.progress_seconds,
            "last_watched_at": record.last_watched_at.isoformat(),
        }




@tool
async def find_latest_video() -> dict:
    """
    查询用户最近观看的任意视频。

    当用户说“继续上次看的”“打开刚才那个”，
    但没有说出具体标题时使用。
    """
    async with AsyncSessionLocal() as session:
        record = await video_service.find_latest_video(session)

    if record is None:
        return {
            "found": False,
            "message": "当前没有任何观看记录。",
        }
    result = {
        "found": True,
        "record_id": record.id,
        "title": record.title,
        "platform": record.platform,
        "url": record.url,
        "position_text": record.position_text,
        "progress_seconds": record.progress_seconds,
        "last_watched_at": record.last_watched_at.isoformat(),
    }
    return result



@tool
def open_video(
    url: str,
    progress_seconds: int = 0,
) -> dict:
    """
    在默认浏览器中打开 Bilibili 视频。

    如果 progress_seconds 大于 0，
    则从对应时间位置继续播放。
    """

    final_url = build_resume_url(
        url=url,
        seconds=progress_seconds,
    )

    opened = webbrowser.open(
        final_url,
        new=2,
        autoraise=True,
    )

    return {
        "opened": opened,
        "url": final_url,
        "progress_seconds": progress_seconds,
        "message": (
            "视频已在默认浏览器中打开。"
            if opened
            else "系统没有确认浏览器已成功打开。"
        ),
    }

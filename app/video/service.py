from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import VideocreateModel
from app.db.models import VideoRecord
from sqlmodel import select, desc
from urllib.parse import urlsplit, parse_qsl, urlunsplit, urlencode


class VideoService:
    async def add_video(self, video_data: VideocreateModel, session: AsyncSession):
        video_data_dict = video_data.model_dump()
        new_video = VideoRecord(**video_data_dict)
        session.add(new_video)
        await session.commit()
        return new_video

    async def find_title_video(self, name: str, session: AsyncSession) -> VideoRecord | None:
        name = name.strip()
        if not name:
            return None
        statement = (
            select(VideoRecord)
            .where(VideoRecord.title.contains(name))
            .order_by(
                desc(VideoRecord.last_watched_at),
                desc(VideoRecord.id),
            )
            .limit(1)
        )
        result = await session.exec(statement)
        return result.first()

    async def find_latest_video(self, session: AsyncSession) -> VideoRecord | None:
        """
        查询最近观看的视频。
        适用于：
        “继续上次看的”
        “打开刚才那个”
        """
        statement = (
            select(VideoRecord)
            .order_by(
                desc(VideoRecord.last_watched_at),
                desc(VideoRecord.id),
            )
            .limit(1)
        )
        result = await session.exec(statement)
        return result.first()


def build_resume_url(
        *,
        platform: str,
        url: str,
        seconds: int,
) -> str:
    """
    根据平台生成带播放进度的 URL。
    """
    if seconds <= 0:
        return url
    platform_name = platform.strip().lower()
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query))
    if platform_name in {
        "bilibili",
        "b站",
        "哔哩哔哩",
    }:
        query["t"] = str(seconds)
    else:
        # 第一版对未知平台使用通用 t 参数。
        query["t"] = str(seconds)

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            urlencode(query),
            parts.fragment,
        )
    )

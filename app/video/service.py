from .schemas import VideocreateModel, VideoProgressReport
from sqlmodel import select, desc
from urllib.parse import urlsplit, parse_qsl, urlunsplit, urlencode
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import VideoRecord


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
        result = await session.execute(statement)
        return result.scalar_one_or_none()

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
        result = await session.execute(statement)
        return result.scalar_one_or_none()


def build_resume_url(
    url: str,
    seconds: int,
) -> str:
    """
    给 Bilibili 视频 URL 添加续播时间参数 t。
    """

    if seconds <= 0:
        return url

    parts = urlsplit(url)

    query = dict(
        parse_qsl(
            parts.query,
            keep_blank_values=True,
        )
    )

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


# 视频观看记录创建和更新
class VideoRecordService:
    async def report_progress(self,
                              session: AsyncSession,
                              payload: VideoProgressReport,
                              ) -> tuple[VideoRecord, bool]:
        """
        创建或更新一条视频观看记录。

        Returns:
            (record, created)
        """
        # 查询观看记录
        statement = select(VideoRecord).where(
            VideoRecord.platform == payload.platform,
            VideoRecord.platform_video_id
            == payload.platform_video_id,
        )

        result = await session.execute(statement)
        record = result.scalar_one_or_none()

        watched_at = payload.reported_at or datetime.now()

        if record is None:
            record = VideoRecord(
                title=payload.title,
                platform=payload.platform,
                platform_video_id=payload.platform_video_id,
                url=str(payload.url),
                progress_seconds=payload.progress_seconds,
                duration_seconds=payload.duration_seconds,
                position_text=VideoRecordService.format_position(
                    payload.progress_seconds
                ),
                last_watched_at=watched_at,
            )

            session.add(record)
            # 处理多个请求同时创建视频造成的异常
            try:
                await session.commit()
            except IntegrityError:
                # 两个请求同时首次创建同一视频时，
                # 唯一约束可能导致其中一个失败。
                await session.rollback()

                result = await session.execute(statement)
                record = result.scalar_one()

                VideoRecordService.apply_progress(
                    record=record,
                    payload=payload,
                    watched_at=watched_at,
                )

                await session.commit()
                await session.refresh(record)

                return record, False

            await session.refresh(record)
            return record, True

        VideoRecordService.apply_progress(
            record=record,
            payload=payload,
            watched_at=watched_at,
        )

        await session.commit()
        await session.refresh(record)

        return record, False

    # 更新视频数据
    @staticmethod
    def apply_progress(
                       *,
                       record: VideoRecord,
                       payload: VideoProgressReport,
                       watched_at: datetime,
                       ) -> None:
        record.title = payload.title
        record.url = str(payload.url)
        record.progress_seconds = payload.progress_seconds
        record.duration_seconds = payload.duration_seconds
        record.position_text = (
            VideoRecordService.format_position(
                payload.progress_seconds
            )
        )
        record.last_watched_at = watched_at

    # 将时间变为人能看懂的时间
    @staticmethod
    def format_position( seconds: int) -> str:
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)

        if hours:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"

        return f"{minutes:02d}:{secs:02d}"

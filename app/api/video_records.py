from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import verify_extension_token
from app.db.main import get_session
from app.video.schemas import (
    VideoProgressReport,
    VideoProgressResponse,
)
from app.video.service import VideoRecordService

video_record_service = VideoRecordService()

video_router = APIRouter(
    prefix="/api/v1/video-records",
    tags=["video-records"],
    dependencies=[
        Depends(verify_extension_token),
    ],
)


# 接收浏览器扩展上报的视频播放进度
@video_router.post(
    "/progress",
    response_model=VideoProgressResponse,
    status_code=status.HTTP_200_OK,
)
async def report_video_progress(
        payload: VideoProgressReport,
        session: Annotated[
            AsyncSession,
            Depends(get_session),
        ],
) -> VideoProgressResponse:

    # 传回元组，true创建新记录，false更新记录
    record, created = await video_record_service.report_progress(
        session=session,
        payload=payload,
    )

    if record.id is None:
        raise RuntimeError(
            "Video record was persisted without an ID."
        )

    return VideoProgressResponse(
        id=record.id,
        created=created,
        title=record.title,
        platform=record.platform,
        progress_seconds=record.progress_seconds,
    )

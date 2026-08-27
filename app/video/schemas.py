from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class VideoSchemas(BaseModel):
    id: int
    title: str                      # 视频名称
    platform: str                   # 视频平台
    url: str                        # 视频原始链接
    position_text: str              # 播放位置
    progress_seconds: int           # 实际播放进度
    last_watched_at: datetime       # 最后一次观看时间
    created_at: datetime            # 创建时间


class VideocreateModel(BaseModel):
    title: str
    platform: str
    url: str
    position_text: str
    progress_seconds: int


class VideoProgressReport(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )
    platform: str = Field(
        min_length=1,
        max_length=50,
    )
    platform_video_id: str = Field(
        min_length=1,
        max_length=255,
    )
    url: HttpUrl
    progress_seconds: int = Field(
        default=0,
        ge=0,
    )
    duration_seconds: int | None = Field(
        default=None,
        ge=0,
    )
    reported_at: datetime | None = None


class VideoProgressResponse(BaseModel):
    id: int
    created: bool
    title: str
    platform: str
    progress_seconds: int


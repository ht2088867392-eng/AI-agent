
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class VideoSchemas(BaseModel):
    id: int
    title: str
    platform: str
    url: str
    position_text: str
    progress_seconds: int
    last_watched_at: datetime
    created_at: datetime

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


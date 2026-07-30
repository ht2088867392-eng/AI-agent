from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field


def utc_now():
    return datetime.now(timezone.utc)


class VideoRecord(SQLModel, table=True):

    __tablename__ = "video_records"
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    title: str
    platform: str
    url: str
    position_text: str
    progress_seconds: int = 0
    last_watched_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime,
            nullable=False,
            default=utc_now,
            onupdate=utc_now,
        )
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(
            DateTime,
            nullable=False,
            default=utc_now,
        )
    )

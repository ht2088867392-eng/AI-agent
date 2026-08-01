from datetime import datetime, timezone
from sqlalchemy import Column, DateTime,UniqueConstraint,BigInteger,Index
from sqlmodel import SQLModel, Field





class VideoRecord(SQLModel, table=True):

    __tablename__ = "video_records"
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    title: str
    platform: str
    platform_video_id: str
    url: str
    position_text: str
    progress_seconds: int = Field(
        default=0,
        sa_type=BigInteger,
    )
    duration_seconds: int | None = Field(
        default=None,
        sa_type=BigInteger,
    )
    last_watched_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            DateTime,
            nullable=False,
            default=datetime.now,

        )
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            DateTime,
            nullable=False,
            default=datetime.now,
        )
    )
    __table_args__ = (
            UniqueConstraint(
                "platform",
                "platform_video_id",
                name="uq_video_platform_video_id",
            ),
            Index(
                "ix_video_records_last_watched_at",
                "last_watched_at",
            ),
        )
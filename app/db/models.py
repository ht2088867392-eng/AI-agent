from datetime import datetime, timezone
from sqlalchemy import Column, DateTime,UniqueConstraint,BigInteger,Index
from sqlmodel import SQLModel, Field


class VideoRecord(SQLModel, table=True):

    __tablename__ = "video_records"
    id: int | None = Field(                     # 视频序号
        default=None,
        primary_key=True,
    )
    title: str                                  # 视频名称
    platform: str                               # 视频平台
    platform_video_id: str                      # 视频在对应平台上的唯一标识
    url: str                                    # 视频链接
    position_text: str                          # 给人看的时间
    progress_seconds: int = Field(              # 实际播放进度
        default=0,
        sa_type=BigInteger,
    )
    duration_seconds: int | None = Field(       # 视频总时长
        default=None,
        sa_type=BigInteger,
    )
    last_watched_at: datetime = Field(          # 最近一次观看时间
        default_factory=datetime.now,
        sa_column=Column(
            DateTime,
            nullable=False,
            default=datetime.now,

        )
    )
    created_at: datetime = Field(               # 创建时间
        default_factory=datetime.now,
        sa_column=Column(
            DateTime,
            nullable=False,
            default=datetime.now,
        )
    )
    __table_args__ = (
            # 唯一约束
            UniqueConstraint(
                "platform",
                "platform_video_id",
                name="uq_video_platform_video_id",
            ),
            # 建立索引
            Index(
                "ix_video_records_last_watched_at",
                "last_watched_at",
            ),
        )
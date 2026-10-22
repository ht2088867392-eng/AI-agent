from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class VideoSchemas(BaseModel):
    """视频记录的完整数据模型，包含数据库自动生成的字段，用于对外返回。"""
    id: int                         # 主键
    title: str                      # 视频名称
    platform: str                   # 视频平台
    url: str                        # 视频原始链接
    position_text: str              # 播放位置
    progress_seconds: int           # 实际播放进度
    last_watched_at: datetime       # 最后一次观看时间
    created_at: datetime            # 创建时间


class VideocreateModel(BaseModel):
    """添加视频记录时的入参模型，只含用户可提供的字段，其余由服务端填充。"""
    title: str                      # 视频名称
    platform: str                   # 视频平台
    url: str                        # 视频原始链接
    position_text: str              # 播放位置（人类可读，如 01:23:45）
    progress_seconds: int           # 实际播放进度（秒）


class VideoProgressReport(BaseModel):
    """浏览器扩展上报播放进度的请求模型，带字段长度与取值范围校验。"""
    title: str = Field(             # 视频名称
        min_length=1,
        max_length=255,
    )
    platform: str = Field(          # 视频平台标识
        min_length=1,
        max_length=50,
    )
    platform_video_id: str = Field(  # 平台内视频唯一ID，与platform共同定位一条记录
        min_length=1,
        max_length=255,
    )
    url: HttpUrl                    # 视频链接，必须是合法的http/https地址
    progress_seconds: int = Field(  # 当前播放进度（秒），不允许为负
        default=0,
        ge=0,
    )
    duration_seconds: int | None = Field(  # 视频总时长（秒），平台未提供时为空
        default=None,
        ge=0,
    )
    reported_at: datetime | None = None    # 扩展侧的上报时间，为空时由服务端取当前时间


class VideoProgressResponse(BaseModel):
    """上报进度接口的响应模型，返回落库后的关键信息。"""
    id: int                         # 记录主键
    created: bool                   # True为新建记录，False为更新已有记录
    title: str                      # 视频名称
    platform: str                   # 视频平台
    progress_seconds: int           # 落库后的播放进度（秒）


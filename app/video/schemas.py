from pydantic import BaseModel
from datetime import date,datetime

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





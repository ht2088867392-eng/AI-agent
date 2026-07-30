
import asyncio

from app.db.main import AsyncSessionLocal
from app.video.schemas import VideocreateModel
from app.video.service import VideoService

video_service = VideoService()
async def seed_videos() -> None:
    videos = [
        {
            "title": "【文曰小强】84分钟速读《三体》大合集",
            "platform": "哔哩哔哩",
            "url": "https://www.bilibili.com/video/BV11s41187QY/?spm_id_from=333.337.search-card.all.click&vd_source=738095cbe9f9d0694d9e7049311626fb",
            "position_text": "第 1 集 ",
            "progress_seconds": 0,
        },
        {
            "title": "黑马程序员python零基础全套教程，8天python从入门到精通，学python看这套就够了",
            "platform": "哔哩哔哩",
            "url": "https://www.bilibili.com/video/BV1qW4y1a7fU/?spm_id_from=333.337.search-card.all.click&vd_source=738095cbe9f9d0694d9e7049311626fb",
            "position_text": "第 1 集",
            "progress_seconds": 0,
        },
    ]

    async with AsyncSessionLocal() as session:
        for item in videos:
            video_data = VideocreateModel(**item)

            new_video = await video_service.add_video(
                video_data=video_data,
                session=session,
            )

            print(f"已添加：{new_video.title}")


if __name__ == "__main__":
    asyncio.run(seed_videos())

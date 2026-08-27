from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.video_records import video_router


app = FastAPI(
    title="AI Video Assistant",
    description='AI助手',
    version="0.1.0",
)


app.add_middleware(
    # CORS跨域
    CORSMiddleware,
    allow_origins=[
         "chrome-extension://fdojgofmlebkpapjbkifkmokedlpcmnb",
    ],
    allow_credentials=False,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "X-Extension-Token",
    ],
)


app.include_router(video_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
    }

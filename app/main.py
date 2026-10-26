from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.agent import get_agent
from app.api.chat_records import chat_router
from app.api.video_records import video_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    async with get_agent() as agent:
        application.state.agent = agent
        yield
    application.state.agent = None


app = FastAPI(
    title="AI Video Assistant",
    description='AI助手',
    version="0.1.0",
    lifespan=lifespan,
)


app.add_middleware(
    # CORS跨域
    CORSMiddleware,
    allow_origins=[
         "chrome-extension://fdojgofmlebkpapjbkifkmokedlpcmnb",
         "http://localhost:3000",
         "http://localhost:5173",
         "http://127.0.0.1:3000",
         "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "X-Extension-Token",
    ],
)


app.include_router(video_router)
app.include_router(chat_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {
        "status": "ok",
    }

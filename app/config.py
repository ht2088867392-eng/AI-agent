from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    DATABASE_URL: str
    browser_extension_token: str
    DB_URI: str
    SILICONFLOW_API_KEY: str
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra='ignore'
    )


Config = Settings()

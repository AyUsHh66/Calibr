from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    GOOGLE_API_KEY: str = "AIzaSyCrOZOdbdf2fd6Hqn6idqEl2LQ-tyneg1c"
    GROQ_API_KEY: str = "gsk_..."
    TAVILY_API_KEY: str = "sk-0123456789abcdef1234567890abcdef"
    DATABASE_URL: str = "sqlite:///./data/calibr.db"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def GEMINI_API_KEY(self) -> str:
        return self.GOOGLE_API_KEY

settings = Settings()
    
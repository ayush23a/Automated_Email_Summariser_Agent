from typing import Literal, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Model Configuration
    MODEL_PROVIDER: Literal["gemini", "groq"] = "gemini"
    MODEL_NAME: str = "gemini-1.5-flash"

    # Gmail Configuration
    GMAIL_CREDENTIALS_PATH: str = "credentials.json"
    GMAIL_TOKEN_PATH: str = "token.json"

    # Application Settings
    TIMEZONE: str = "Asia/Kolkata"
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting & Volume Control
    MAX_EMAILS_TO_FETCH: int = 50  # Max emails to process per run (0 = unlimited)
    API_DELAY_SECONDS: float = 2.0  # Delay between LLM API calls
    MAX_RETRIES: int = 3  # Max retries for failed API calls

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()

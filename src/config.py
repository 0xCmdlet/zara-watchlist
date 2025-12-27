# src/config.py

from dataclasses import dataclass

@dataclass
class Settings:
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
    timeout_seconds: int = 15

settings = Settings()

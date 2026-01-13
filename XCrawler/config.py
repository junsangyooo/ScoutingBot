"""
X API V2 Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)


class XAPIConfig:
    """X API V2 Configuration"""

    # API Credentials
    BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
    API_KEY = os.getenv("X_API_KEY")
    API_SECRET = os.getenv("X_API_SECRET")
    ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

    # Monitoring Settings
    POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))

    # API Endpoints
    BASE_URL = "https://api.twitter.com/2"

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.BEARER_TOKEN:
            raise ValueError(
                "X_BEARER_TOKEN is required. "
                "Please set it in .env file or environment variables."
            )
        return True

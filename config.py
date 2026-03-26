import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

class Config:
    """Centralized configuration class. All env vars are loaded here."""
    
    # 1. Flask Settings
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-dev-key-change-in-production")
    
    # 2. Database Settings
    DB_HOST = os.environ.get("DB_HOST")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_NAME = os.environ.get("DB_NAME")
    
    # 3. External API Keys (Supabase & OpenAI)
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    @classmethod
    def validate(cls):
        """
        Runs on startup to ensure all critical variables exist.
        This prevents the app from crashing mysteriously later!
        """
        critical_vars = {
            "DB_HOST": cls.DB_HOST,
            "DB_USER": cls.DB_USER,
            "DB_NAME": cls.DB_NAME,
            "SUPABASE_URL": cls.SUPABASE_URL,
            "SUPABASE_KEY": cls.SUPABASE_KEY,
            "OPENAI_API_KEY": cls.OPENAI_API_KEY
        }
        
        missing = [name for name, val in critical_vars.items() if not val]
        
        if missing:
            raise ValueError(
                f"🚨 CRITICAL ERROR: The following environment variables are missing "
                f"from your .env file or host environment: {', '.join(missing)}"
            )
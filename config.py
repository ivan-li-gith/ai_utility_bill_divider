import os
from dotenv import load_dotenv

load_dotenv()

class Config:    
    SECRET_KEY = os.environ.get("SECRET_KEY", "fallback-dev-key-change-in-production")
    DB_HOST = os.environ.get("DB_HOST")
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    DB_NAME = os.environ.get("DB_NAME")
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

    # runs on startup to make sure variables exist
    @classmethod
    def validate(cls):
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
                f"The following environment variables are missing "
                f"from your .env file or host environment: {', '.join(missing)}"
            )
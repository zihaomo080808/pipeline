import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    DATABASE_URL     = os.getenv("DATABASE_URL", "sqlite:///oppradar.db")
    AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    AIRTABLE_TABLE   = os.getenv("AIRTABLE_TABLE_NAME")

settings = Settings()

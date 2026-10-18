from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    ALGORITHM = os.getenv("ALGORITHM")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    scheme = os.getenv("scheme")
    paas_for_cookies = os.getenv("paas_for_cookies")

settings = Settings()

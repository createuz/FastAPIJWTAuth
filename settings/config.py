import os
from dotenv import load_dotenv
from datetime import timedelta
from typing import List

load_dotenv()


class Config:
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_MODELS: List[str] = ["settings.models"]
    DB_URL = f"postgres://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SECRET_KEY = 'secret'
    ALGORITHM = "HS256"
    JWT_ACCESS_EXP = timedelta(minutes=15)
    JWT_REFRESH_EXP = timedelta(days=30)

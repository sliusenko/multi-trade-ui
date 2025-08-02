import os
from databases import Database

DB_USER = os.getenv("DB_USER", "bot")
DB_PASS = os.getenv("DB_PASS", "00151763Db3c")
DB_HOST = os.getenv("DB_HOST", "172.19.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "multi_trade_bot")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Async Database instance
database = Database(DATABASE_URL)

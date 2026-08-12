#Import dependensi yang diperlukan

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variable dari file .env
load_dotenv(find_dotenv())


# Mengambil URL basis data dari enviroment variable
sqlalchemy_database_url = os.getenv("DATABASE_URL")

# Membuat engine sqlalchemy
engine = create_async_engine(sqlalchemy_database_url)

# Membuat session
async_session = sessionmaker(engine, expire_on_commit = False, class_ = AsyncSession)

# Membuat base model
Base = declarative_base()

# Fungsi untuk mendapatkan session database
async def get_db() -> AsyncSession:
    async with async_session() as db:
        yield db


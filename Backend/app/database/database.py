#Import dependensi yang diperlukan
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variable dari file .env
load_dotenv(find_dotenv())


# Mengambil URL basis data dari enviroment variable
sqlalchemy_database_url = os.getenv("DATABASE_URL")

# Membuat engine sqlalchemy
engine = create_engine(sqlalchemy_database_url)

# Membuat session
session_local = sessionmaker(autocommit = False, autoflush = False, bind = engine)

# Membuat base model
Base = declarative_base()

# Fungsi untuk mendapatkan session database
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()
        


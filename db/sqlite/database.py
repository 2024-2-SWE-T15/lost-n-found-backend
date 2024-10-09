import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import Base

load_dotenv("config/.env")


# DATABASE_URL = f'sqlite:///:memory:'
# DATABASE_URL = f'sqlite:////data/app/sqlite/dataCache.db'
DATABASE_URL = f'sqlite:///{os.getenv("DATABASE_PATH")}'

def initDB():
  engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

  # Connect to the MySQL database
  SessionLocal = sessionmaker(autoflush=False, bind=engine)
  Base.metadata.create_all(bind=engine)
  return SessionLocal

SessionLocal = initDB()

def getDB():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

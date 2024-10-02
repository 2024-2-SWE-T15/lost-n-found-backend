from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import Base

# DATABASE_URL = f'sqlite:///:memory:'
# DATABASE_URL = f'sqlite:////data/app/sqlite/dataCache.db'
DATABASE_URL = f'sqlite:///.temp/cache.db'

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

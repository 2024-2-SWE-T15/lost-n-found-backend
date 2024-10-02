import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .model import Base

load_dotenv('config/.env')

ID = os.getenv('MYSQL_ID')
PW = os.getenv('MYSQL_PW')
HOST = os.getenv('MYSQL_HOST')
PORT = int(os.getenv('MYSQL_PORT'))
MIN = int(os.getenv('MYSQL_MIN'))
MAX = int(os.getenv('MYSQL_MAX'))
DATABASE = os.getenv('MYSQL_DATABASE')

DATABASE_URL = f'mysql+mysqldb://{ID}:{PW}@{HOST}:{PORT}/{DATABASE}'

def initDB():
  
  """
  Initializes the database connection and creates all tables.

  Returns:
    SessionLocal (sessionmaker): A configured sessionmaker instance bound to the engine.
  """
  engine = create_engine(DATABASE_URL, pool_size=MIN, max_overflow=MAX)

  # Connect to the MySQL database
  SessionLocal = sessionmaker(autoflush=False, bind=engine)
  Base.metadata.create_all(bind=engine)
  return SessionLocal
  
SessionLocal = initDB()

def getDB():
  """
  Returns a database session.

  This function creates a new database session using the `SessionLocal` object and yields it.
  After the caller is done using the session, the session is closed.

  Yields:
    SessionLocal: A database session.

  """
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()


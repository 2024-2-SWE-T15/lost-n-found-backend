from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.sqlite import model as sqlite_model
from db.sqlite import crud as sqlite_crud
from db.sqlite import database as sqlite_db

def regularClear():
  SessionLocal = sqlite_db.initDB()
  db: Session = SessionLocal()
  try:
    sqlite_crud.clearAccessToken(db)
  finally:
    db.close()
  

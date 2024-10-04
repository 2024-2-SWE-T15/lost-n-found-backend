from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.sqlite import database as sqlite_db
from db.sqlite import model as sqlite_model
from db.sqlite import crud as sqlite_crud



def regularClear():
  SessionLocal = sqlite_db.initDB()
  db: Session = SessionLocal()
  try:
    sqlite_crud.clearAccessToken(db)
  finally:
    db.close()
  

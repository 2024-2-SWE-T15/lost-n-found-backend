from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud

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
  
def suggestion():
  
  pass
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .model import RefreshedToken
from .schema import RefreshedTokenSchema

# Cache CRUD
def addRefreshedToken(db: Session, refresh_token: str):
  dbItem = RefreshedToken(refresh_token=refresh_token, create_time=datetime.now())
  db.add(dbItem)
  db.commit()
  db.refresh(dbItem)
  return dbItem

def getRefreshedToken(db: Session, refresh_token: str):
  dbItem = db.query(RefreshedToken).filter(RefreshedToken.refresh_token == refresh_token).first()
  return dbItem

def getAllRefreshedToken(db: Session):
  return db.query(RefreshedToken).all()

def clearRefreshedToken(db: Session):
  dbItems = db.query(RefreshedToken).filter(RefreshedToken.create_time < datetime.now() - timedelta(minutes=15)).all()
  for item in dbItems:
    try:
      db.delete(item)
      db.commit()
    except SQLAlchemyError:
      db.rollback()
      pass
  return True


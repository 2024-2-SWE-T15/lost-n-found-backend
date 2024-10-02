from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .model import InvalidToken
from .schema import InvalidTokenSchema

# Cache CRUD
def addInvalidAccessToken(db: Session, access_token: str):
  dbItem = InvalidToken(access_token=access_token, create_time=datetime.now())
  db.add(dbItem)
  db.commit()
  db.refresh(dbItem)
  return dbItem

def getInvalidAccessToken(db: Session, access_token: str):
  dbItem = db.query(InvalidToken).filter(InvalidToken.access_token == access_token).first()
  return dbItem

def getAllInvalidAccessToken(db: Session):
  return db.query(InvalidToken).all()

def clearAccessToken(db: Session):
  dbItems = db.query(InvalidToken).filter(InvalidToken.create_time < datetime.now() - timedelta(days=3)).all()
  for item in dbItems:
    try:
      db.delete(item)
      db.commit()
    except SQLAlchemyError:
      db.rollback()
      pass
  return True

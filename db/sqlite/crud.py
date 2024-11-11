from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .model import RefreshedToken, CSRFToken
from .schema import RefreshedTokenSchema, CSRFTokenSchema

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

# CSRF Token CRUD
def addCSRFToken(db: Session, csrf_token: str, redirect_url: str):
  dbItem = CSRFToken(csrf_token=csrf_token, redirect_url=redirect_url, create_time=datetime.now())
  db.add(dbItem)
  db.commit()
  db.refresh(dbItem)
  return dbItem

def getCSRFToken(db: Session, csrf_token: str):
  dbItem = db.query(CSRFToken).filter(CSRFToken.csrf_token == csrf_token).first()
  return dbItem

def getAllCSRFToken(db: Session):
  return db.query(CSRFToken).all()

def removeCSRFToken(db: Session, csrf_token: str):
  dbItem = db.query(CSRFToken).filter(CSRFToken.csrf_token == csrf_token).first()
  try:
    db.delete(dbItem)
    db.commit()
  except SQLAlchemyError:
    db.rollback()
    return False
  return True

def clearCSRFToken(db: Session):
  dbItems = db.query(CSRFToken).filter(CSRFToken.create_time < datetime.now() - timedelta(minutes=15)).all()
  for item in dbItems:
    try:
      db.delete(item)
      db.commit()
    except SQLAlchemyError:
      db.rollback()
      pass
  return True


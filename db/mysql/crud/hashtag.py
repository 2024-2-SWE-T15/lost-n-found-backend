from datetime import datetime

from fuzzywuzzy import process

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..model import Hashtag


def get(db: Session, hashtag: str):
  db_item = db.query(Hashtag).filter(Hashtag.name == hashtag).first()
  return db_item

def register(db: Session, hashtag: str):
  db_item = Hashtag(
    name=hashtag,
    last_access=datetime.now()
  )
  db.add(db_item)
  db.commit()
  db.refresh(db_item)
  return db_item

def fuzzyMatch(db: Session, query: str, excepts: list):
  db_items = db.query(Hashtag).all()
  if excepts:
    db_items = [item.name for item in db_items if item.name not in excepts]
  else:
    db_items = [item.name for item in db_items]
  return process.extract(query, db_items, limit=len(db_items))

def update(db: Session, hashtag: str):
  db_item = db.query(Hashtag).filter(Hashtag.name == hashtag).first()
  db_item.last_access = datetime.now()
  db.commit()
  db.refresh(db_item)
  return db_item
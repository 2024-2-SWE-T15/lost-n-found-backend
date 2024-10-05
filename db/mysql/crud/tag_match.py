from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..model import TagMatch
from ..schema import TagMatchSchema


def get(db: Session, post_id: str):
  db_items = db.query(TagMatch).filter(TagMatch.post_id == post_id).all()
  return [tagmatch.tag_name for tagmatch in db_items]

def getByTag(db: Session, tags: list[str]):
  query = db.query(TagMatch)
  for tag in tags:
    query = query.filter(TagMatch.tag_name == tag)
  db_items = query.all()
  return db_items

def getAll(db: Session):
  return db.query(TagMatch).all()

def register(db: Session, tag_match: TagMatchSchema):
  db_item = TagMatch(
    post_id=tag_match.post_id,
    tag_name=tag_match.tag_name,
  )
  db.add(db_item)
  db.commit()
  db.refresh(db_item)
  return db_item
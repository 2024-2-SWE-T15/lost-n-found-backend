from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..model import FoundView


def get(db: Session, post_id: str):
  db_item = db.query(FoundView).filter(FoundView.id == post_id).first()
  return db_item

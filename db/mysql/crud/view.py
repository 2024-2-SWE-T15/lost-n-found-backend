from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..model import PostView


def get(db: Session, post_id: str):
  db_item = db.query(PostView).filter(PostView.id == post_id).first()
  return db_item

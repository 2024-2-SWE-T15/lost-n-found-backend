from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..model import Kept
from ..schema import KeptSchema

from .stronghold import get as getStronghold


def get(db: Session, post_id: str):
  db_item = db.query(Kept).filter(Kept.post_id == post_id).first()
  return db_item

def register(db: Session, kept: KeptSchema):
  if kept.stronghold_id:
    db_item = Kept(
      post_id=kept.post_id,
      coordinates=getStronghold(db, kept.stronghold_id).coordinates,
      stronghold_id=kept.stronghold_id
    )
  else:
    db_item = Kept(
      post_id=kept.post_id,
      coordinates=kept.coordinates,
      stronghold_id=None
    )
  
  db.add(db_item)
  db.commit()
  db.refresh(db_item)
  return db_item
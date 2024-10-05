from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..model import Identity
from ..schema import IdentitySchema
from ..schema import IdentitySchemaGet


def get(db: Session, identity: IdentitySchemaGet):
  db_item = db.query(Identity).filter(Identity.post_id == identity.post_id, Identity.name == identity.name).first()
  return db_item


def getAll(db: Session, post_id: str):
  db_items = db.query(Identity).filter(Identity.post_id == post_id).all()
  return db_items

def register(db: Session, identity: IdentitySchema):
  db_item = Identity(
    post_id=identity.post_id,
    name=identity.name,
    value=identity.value,
  )
  db.add(db_item)
  db.commit()
  db.refresh(db_item)
  return db_item
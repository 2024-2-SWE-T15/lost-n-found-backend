from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..model import Identity
from ..schema import IdentitySchema
from ..schema import IdentitySchemaMatch


def get(db: Session, identity: IdentitySchema):
  db_item = db.query(Identity).filter(Identity.post_id == identity.post_id, Identity.name == identity.name).first()
  return db_item


def getAll(db: Session, post_id: str):
  db_items = db.query(Identity).filter(Identity.post_id == post_id).all()
  id_dict = {}
  for db_item in db_items:
    id_dict[db_item.name] = db_item.value
  return id_dict

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

def match(db: Session, identity: IdentitySchema):
  db_item = db.query(Identity).filter(Identity.post_id == identity.post_id, Identity.name == identity.name).first()
  if db_item:
    db_item.value = identity.value
    db.commit()
    db.refresh(db_item)
    return db_item
  return None

def update(db: Session, identity: IdentitySchema):
  db_item = db.query(Identity).filter(Identity.post_id == identity.post_id, Identity.name == identity.name).first()
  db_item.value = identity.value
  db.commit()
  db.refresh(db_item)
  return db_item

def delete(db: Session, identity: IdentitySchema):
  db_item = db.query(Identity).filter(Identity.post_id == identity.post_id, Identity.name == identity.name).first()
  try:
    db.delete(db_item)
    db.commit()
    return True
  except SQLAlchemyError:
    db.rollback()
  return False
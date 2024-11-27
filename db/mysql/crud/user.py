from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from ..model import User
from ..schema import UserSchema
from ..schema import UserSchemaAdd, UserSchemaGet


def register(db: Session, user: UserSchemaAdd):
  db_item = User(id=user.id, platform=user.platform, 
                nickname=user.nickname, 
                profile_image_url=user.profile_image_url, 
                create_time=datetime.now(),
                email=user.email)
  db.add(db_item)
  db.commit()
  db.refresh(db_item)
  return db_item

def get(db: Session, user: UserSchemaGet):
  db_item = db.query(User).filter(User.id == user.id).first()
  return db_item

def update(db: Session, user: UserSchema):
  db_item = db.query(User).filter(User.id == user.id, User.platform == user.platform).first()
  if user.nickname:
    db_item.nickname = user.nickname
  if user.profile_image_url:
    db_item.profile_image_url = user.profile_image_url
  if user.email:
    db_item.email = user.email
  db_item.update_time = datetime.now()
  db.commit()
  db.refresh(db_item)
  return db_item

def delete(db: Session, user: UserSchemaGet):
  try:
    db.query(User).filter(User.id == user.id, User.platform == user.platform).delete()
    db.commit()
    return True
  except SQLAlchemyError as e:
    db.rollback()
    return False
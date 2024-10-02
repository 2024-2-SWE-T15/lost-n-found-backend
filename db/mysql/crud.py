from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


from .model import User
from .schema import UserSchema
from .schema import UserSchemaAdd, UserSchemaGet

# User CRUD
def registerUser(db: Session, user: UserSchemaAdd):
  dbItem = User(id=user.id, platform=user.platform, 
                nickname=user.nickname, 
                profile_image_url=user.profile_image_url, 
                create_time=datetime.now())
  db.add(dbItem)
  db.commit()
  db.refresh(dbItem)
  return dbItem

def getUser(db: Session, user: UserSchemaGet):
  dbItem = db.query(User).filter(User.id == user.id, User.platform == user.platform).first()
  return dbItem

def updateUser(db: Session, user: UserSchema):
  dbItem = db.query(User).filter(User.id == user.id, User.platform == user.platform).first()
  if user.nickname:
    dbItem.nickname = user.nickname
  if user.profile_image_url:
    dbItem.profile_image_url = user.profile_image_url
  dbItem.update_time = datetime.now()
  db.commit()
  db.refresh(dbItem)
  return dbItem
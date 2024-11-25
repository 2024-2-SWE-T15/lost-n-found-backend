from fastapi import APIRouter, Depends, Request, Response, HTTPException, Query, Form

from sqlalchemy.orm import Session

from modules.utils import parsePointString, point2Tuple, tuple2PointString, convertTuple2Zone

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema


def getProfile(db: Session, user_id: str):
  db_item = db.query(mysql_model.Profile).filter(mysql_model.Profile.user_id == user_id).first()
  return db_item

def registerProfile(db: Session, profile: mysql_schema.ProfileSchema):
  item = mysql_model.Profile(user_id=profile.user_id,
                             data=profile.data)
  db.add(item)
  db.commit()
  db.refresh(item)
  return item

def updateProfile(db: Session, profile: mysql_schema.ProfileSchema):
  item = db.query(mysql_model.Profile).filter(mysql_model.Profile.user_id == profile.user_id).first()
  item.data = profile.data
  db.commit()
  db.refresh(item)
  return item

def deleteProfile(db: Session, user_id: str):
  item = db.query(mysql_model.Profile).filter(mysql_model.Profile.user_id == user_id).first()
  db.delete(item)
  db.commit()
  return item
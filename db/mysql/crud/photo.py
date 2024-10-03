from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..model import Photo
from ..schema import PhotoSchema


def get(db: Session, photo_id: str):
  db_item = db.query(Photo).filter(Photo.id == photo_id).first()
  return db_item

def register(db: Session, photo: PhotoSchema):
  db_item = Photo(
    id=photo.id,
    post_id=photo.post_id,
    extension=photo.extension,
    data=photo.data,
  )
  db.add(db_item)
  db.commit()
  db.refresh(db_item)
  return db_item
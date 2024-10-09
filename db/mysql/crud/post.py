import os
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..model import Post
from ..schema import PostSchema


def get(db: Session, post_id: str):
  db_item = db.query(Post).filter(Post.id == post_id).first()
  return db_item


def search(db: Session, postSchema: PostSchema):
  query = db.query(Post)
  if postSchema.valid is not None:
    query = query.filter(Post.valid == postSchema.valid)
  if postSchema.user_id:
    query = query.filter(Post.user_id == postSchema.user_id)
  if postSchema.update_time:
    query = query.filter(Post.update_time + timedelta(days=int(os.getenv('POST_EXPIRED'))) < postSchema.update_time)
  if postSchema.is_lost:
    query = query.filter(Post.is_lost == postSchema.is_lost)
  
  db_item = query.all()
  return db_item


def register(db: Session, post: PostSchema):
  db_item = Post(
    title=post.title,
    user_id=post.user_id,
    coordinates=post.coordinates,
    description=post.description,
    create_time=datetime.now(),
    is_lost=post.is_lost
  )
  db.add(db_item)
  db.commit()
  db.refresh(db_item)
  return db_item

def update(db: Session, post_id: str, post: PostSchema):
  db_item = db.query(Post).filter(Post.id == post_id).first()
  db_item.title = post.title
  db_item.coordinates = post.coordinates
  db_item.description = post.description
  db_item.update_time = datetime.now()
  db.commit()
  db.refresh(db_item)
  return db_item

def delete(db: Session, post_id: str):
  db_item = db.query(Post).filter(Post.id == post_id).first()
  db.delete(db_item)
  db.commit()
  return db_item
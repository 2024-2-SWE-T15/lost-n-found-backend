from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from .suggest import suggestion


async def updateMatchRank():
  SessionLocal = mysql_db.initDB()
  db: Session = SessionLocal()
  try:
    altered_posts = []
    
    posts = mysql_crud.post.search(db, mysql_model.Post(valid=True, is_lost=True))
    for post in posts:
      if post.update_time + timedelta(days=1) < datetime.now():
        post.update_time += timedelta(days=1)
        post.match_rank += 1
        altered_posts.append(post.id)
        mysql_crud.post.update(db, post)
    
    await suggestion(altered_posts, is_lost=True)
  finally:
    db.close()
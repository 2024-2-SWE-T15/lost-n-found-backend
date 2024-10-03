from datetime import datetime

from fuzzywuzzy import process

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2 import WKTElement

from ..model import Hashtag, Post, TagMatch
from ..schema import PostSchemaSearch


def get(db: Session, search: PostSchemaSearch):
  query = db.query(Post).filter(Post.valid == True)
  if search.is_lost is not None:
    query = query.filter(Post.is_lost == search.is_lost)
  if search.tags:
    query = query.join(TagMatch).filter(TagMatch.tag_name.in_(search.tags))
  if search.coordinates:
    distance = search.distance if search.distance else 50.0
    query = query.filter(
      func.ST_Distance_Sphere(Post.coordinates, WKTElement(search.coordinates, srid=4326)) <= search.distance
    )
  db_items = query.all()
  return db_items

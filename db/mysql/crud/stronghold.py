from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2 import WKTElement

from modules.utils import haversineDistance, haversineSquare, tuple2PointString

from ..model import Stronghold
from ..schema import StrongholdSchema
from ..schema import CoordinateSchema


def get(db: Session, stronghold_id: str):
  db_item = db.query(Stronghold).filter(Stronghold.id == stronghold_id).first()
  return db_item

def post(db: Session, stronghold: StrongholdSchema):
  db_item = Stronghold(
    name=stronghold.name,
    coordinates=stronghold.coordinates,
    description=stronghold.description,
  )
  db.add(db_item)
  db.commit()
  db.refresh(db_item)
  return db_item

def withinDistance(db: Session, search_range: CoordinateSchema):
  db_items = db.query(Stronghold).filter(
    func.ST_Distance_Sphere(Stronghold.coordinates, WKTElement(tuple2PointString(search_range.coordinates), srid=4326)) <= search_range.distance
  ).all()
  return db_items

def withinZone(db: Session, search_range: CoordinateSchema):
  # by zone system, not implemented
  return None
  db_items = db.query(Stronghold).filter(
    
  ).all()
  return db_items
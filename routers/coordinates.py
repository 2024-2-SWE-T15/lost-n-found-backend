import os

from fastapi import APIRouter, Depends, Request, Response, HTTPException, Query

from sqlalchemy.orm import Session

from modules.utils import parsePointString, point2Tuple, tuple2PointString, convertTuple2Zone

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from .dependencies import getCurrentUser
from .coordinates_func import router as func_routers


router = APIRouter(prefix='/marker', tags=['Marker'])

@router.get('/')
async def getCoordinates(lng: float = Query(...), 
                         lat: float = Query(...),
                         distance: float = Query(...),
                         db: Session = Depends(mysql_db.getDB)):
  
  items = mysql_crud.search.getByCoordinates(db, (lng, lat), distance)
  for item in items:
    item.coordinates = point2Tuple(item.coordinates)
  
  return items

router.include_router(func_routers)
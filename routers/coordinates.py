import os

from fastapi import APIRouter, Depends, Request, Response, HTTPException, Query

from sqlalchemy.orm import Session

from modules.utils import thumbnail, img2DataURL, point2TupleStructure

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from .dependencies import getCurrentUser
from .coordinates_func import router as func_routers


router = APIRouter(prefix='/marker', tags=['Marker'])

@router.get('/')
async def getCoordinates(lat: float = Query(...), 
                         lng: float = Query(...),
                         distance: float = Query(...),
                         db: Session = Depends(mysql_db.getDB)):
  if lat < -90 or lat > 90 or lng < -180 or lng > 180:
    raise HTTPException(status_code=400, detail='Invalid coordinates')
  
  items = mysql_crud.search.getByCoordinates(db, (lat, lng), distance)
  for i, item in enumerate(items):
    items[i] = point2TupleStructure(item)
    
    photo = mysql_crud.photo.getAll(db, item.id)
    if photo:
      items[i].thumbnail = img2DataURL('png', thumbnail(mysql_crud.photo.get(db, photo[0]).data))
    
    items[i].hashtags = mysql_crud.tag_match.getAll(db, item.id)
  
  return items

router.include_router(func_routers)
import os

from fastapi import APIRouter, Depends, Request, Response, HTTPException, Query, Form

from sqlalchemy.orm import Session

from modules.utils import parsePointString, point2Tuple, tuple2PointString, convertTuple2Zone

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from ..dependencies import getCurrentUser


router = APIRouter(prefix='/stronghold', tags=['Stronghold Marker'])

@router.get('/')
async def getStrongholds(lat: float = Query(...), 
                         lng: float = Query(...),
                         distance: float = Query(...),
                         db: Session = Depends(mysql_db.getDB)):
  if lat < -90 or lat > 90 or lng < -180 or lng > 180:
    raise HTTPException(status_code=400, detail='Invalid coordinates')
    
  items = mysql_crud.stronghold.withinDistance(db, (lat, lng), distance)
  for item in items:
    item.coordinates = point2Tuple(item.coordinates)
  
  return items

@router.post('/')
async def registerStronghold(stronghold: mysql_schema.StrongholdSchemaAdd = Form(...),
                             user: mysql_model.User = Depends(getCurrentUser),
                             db: Session = Depends(mysql_db.getDB)):
  item = mysql_crud.stronghold.post(db, mysql_model.Stronghold(name=stronghold.name,
                                                               coordinates=(stronghold.lat, stronghold.lng),
                                                               description=stronghold.description))
  item.coordinates = point2Tuple(item.coordinates)
  return item
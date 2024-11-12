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
async def getStrongholds(base: mysql_schema.CoordinateSchema = Query(...),
                         db: Session = Depends(mysql_db.getDB)):
    
  items = mysql_crud.stronghold.withinDistance(db, base)
  for item in items:
    item.coordinates = point2Tuple(item.coordinates)
  
  return items

@router.post('/')
async def registerStronghold(stronghold: mysql_schema.StrongholdSchema = Form(...),
                             user: mysql_model.User = Depends(getCurrentUser),
                             db: Session = Depends(mysql_db.getDB)):
  item = mysql_crud.stronghold.post(db, stronghold)
  item.coordinates = point2Tuple(item.coordinates)
  return item
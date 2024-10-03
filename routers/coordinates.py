import os
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, Request, Response, HTTPException

from sqlalchemy.orm import Session

from modules.utils import parsePointString, point2Tuple, tuple2PointString, convertTuple2Zone

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from .dependencies import getCurrentUser
from .coordinates_func import router as func_routers

router = APIRouter(prefix='/lostnfound', tags=['LostNFound'])


@router.get('/')
async def getCoordinates(
                         db: Session = Depends(mysql_db.getDB)):
    
    
    item = mysql_crud.stronghold.get(db, '1')
    print(type(item.coordinates))
    item.coordinates = point2Tuple(item.coordinates)
    print(type(item.coordinates))
    print("{:.7f} {:.7f}".format(item.coordinates[0], item.coordinates[1]))
    zone = convertTuple2Zone(item.coordinates, gap=0.00002)
    print("{:.7f} {:.7f}".format(zone[0], zone[1]))
    
    # items = mysql_crud.stronghold.withinDistance(db, mysql_schema.CoordinateSchema(coordinates=(37.7749, -122.41942), distance=10))
    # # items[0].coordinates = point2Tuple(items[0].coordinates)
    # print(type(items[0].coordinates))
    
    return zone


router.include_router(func_routers)
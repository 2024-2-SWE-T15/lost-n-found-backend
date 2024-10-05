import os
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, Request, Response, HTTPException, Query

from sqlalchemy.orm import Session

from modules.utils import parsePointString, point2Tuple, tuple2PointString, convertTuple2Zone

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema


router = APIRouter(prefix='/hashtag', tags=['Hashtag'])

@router.get('/search')
async def searchHashtag(query: str = Query(...), 
                     db: Session = Depends(mysql_db.getDB)):
  return mysql_crud.hashtag.fuzzyMatch(db, query)


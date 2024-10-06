
from fastapi import APIRouter, Response, HTTPException, Depends, Query, Form

from sqlalchemy.orm import Session

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from tasks.suggest import suggestion

from routers.dependencies import loadUser


router = APIRouter(prefix='/{post_id}/personal_id', tags=['Post-Personal-ID'])

@router.get('/')
async def getIdentityList(post_id: str,
                        db: Session = Depends(mysql_db.getDB)):
  identity_list = mysql_crud.identity.getAll(db, post_id)
  return [identity.name for identity in identity_list]


@router.post('/')
async def matchIdentity(post_id: str,
                        identity: mysql_schema.IdentitySchemaMatch = Form(...),
                        db: Session = Depends(mysql_db.getDB)):

  if not (identity := mysql_crud.identity.get(db, mysql_model.Identity(post_id=post_id, name=identity.name, value=identity.value))):
    raise HTTPException(status_code=500, detail='Failed to match personal ID')
  
  return identity
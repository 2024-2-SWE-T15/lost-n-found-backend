
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


@router.post('/{identity_name}')
async def registerIdentity(post_id: str,
                           identity_name: str,
                           value: str = Form(...),
                           user: mysql_model.User = Depends(loadUser),
                           db: Session = Depends(mysql_db.getDB)):
  if not (post := mysql_crud.post.get(db, post_id)):
    raise HTTPException(status_code=404, detail='Post not found')
  
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='Permission denied')

  if not (identity := mysql_crud.identity.register(db, mysql_model.Identity(post_id=post_id, name=identity_name, value=value))):
    raise HTTPException(status_code=500, detail='Failed to register personal ID')
  
  return identity

@router.put('/{identity_name}')
async def updateIdentity(post_id: str,
                         identity_name: str,
                         value: str = Form(...),
                         user: mysql_model.User = Depends(loadUser),
                         db: Session = Depends(mysql_db.getDB)):
  if not (post := mysql_crud.post.get(db, post_id)):
    raise HTTPException(status_code=404, detail='Post not found')
  
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='Permission denied')

  if not (identity := mysql_crud.identity.match(db, mysql_model.Identity(post_id=post_id, name=identity_name, value=value))):
    raise HTTPException(status_code=500, detail='Failed to update personal ID')
  
  return identity

@router.delete('/{identity_name}')
async def deleteIdentity(post_id: str,
                         identity_name: str,
                         user: mysql_model.User = Depends(loadUser),
                         db: Session = Depends(mysql_db.getDB)):
  if not (post := mysql_crud.post.get(db, post_id)):
    raise HTTPException(status_code=404, detail='Post not found')
  
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='Permission denied')

  if not mysql_crud.identity.delete(db, mysql_model.Identity(post_id=post_id, name=identity_name)):
    raise HTTPException(status_code=500, detail='Failed to delete personal ID')
  
  return Response(status_code=204)
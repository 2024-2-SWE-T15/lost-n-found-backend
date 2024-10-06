from fastapi import APIRouter, Response, HTTPException, Depends, Query, Form

from sqlalchemy.orm import Session

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from routers.dependencies import loadUser


router = APIRouter(prefix='/hashtag', tags=['Post-Hashtag'])

@router.get('/')
async def getHashtags(post_id: str,
                      db: Session = Depends(mysql_db.getDB)):
  return mysql_crud.tag_match.getAll(db, post_id)

@router.post('/')
async def registerHashtag(post_id: str,
                          tag_name: str = Form(...),
                          user: mysql_model.User = Depends(loadUser),
                          db: Session = Depends(mysql_db.getDB)):
  if not (post := mysql_crud.post.get(db, post_id)):
    raise HTTPException(status_code=404, detail='Post not found')
  
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='Permission denied')
  
  if not mysql_crud.tag_match.register(db, mysql_model.TagMatch(post_id=post_id, tag_name=tag_name)):
    raise HTTPException(status_code=400, detail='Already registered tag')
  
  return tag_name

@router.delete('/')
async def deleteHashtag(post_id: str,
                        tag_name: str,
                        user: mysql_model.User = Depends(loadUser),
                        db: Session = Depends(mysql_db.getDB)):
  if not (post := mysql_crud.post.get(db, post_id)):
    raise HTTPException(status_code=404, detail='Post not found')
  
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='Permission denied')


  if not mysql_crud.tag_match.delete(db, mysql_model.TagMatch(post_id=post_id, tag_name=tag_name)):
    raise HTTPException(status_code=400, detail='Not matched tag')
  
  return Response(status_code=204)
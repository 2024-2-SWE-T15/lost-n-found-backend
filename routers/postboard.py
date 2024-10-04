

from fastapi import APIRouter, Response, HTTPException, Depends, Query, Form

from sqlalchemy.orm import Session

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from modules.utils import point2TupleStructure, tuple2Point, tuple2PointString, postImgName, dataURL2Img

from .dependencies import loadUser

from . import post_func

router = APIRouter(prefix='/post', tags=['Post'])

@router.get('/')
async def getPost(post_id: str = Query(...),
                  db: Session = Depends(mysql_db.getDB)):
  post = mysql_crud.post.get(db, post_id)
  if not post:
    raise HTTPException(status_code=404, detail='Post not found')
  return post


@router.post('/')
async def registerPost(postSchemaAdd: mysql_schema.PostSchemaAdd,
                    user: mysql_model.User = Depends(loadUser),
                    db: Session = Depends(mysql_db.getDB)):
  if not postSchemaAdd.is_lost:
    if not postSchemaAdd.kept_coordinates and not postSchemaAdd.stronghold_id:
      raise HTTPException(status_code=400, detail='Invalid coordinates')

  for photo in postSchemaAdd.photos:
    if not isinstance(photo, str) or not photo.startswith('data:image/'):
      raise HTTPException(status_code=400, detail='Invalid photo')

  if not (post := mysql_crud.post.register(db, mysql_model.Post(title=postSchemaAdd.title, 
                                                                user_id=user.id, 
                                                                coordinates=tuple2PointString(postSchemaAdd.coordinates), 
                                                                description=postSchemaAdd.description,
                                                                is_lost=postSchemaAdd.is_lost))):
    raise HTTPException(status_code=500, detail='Failed to register post')
  
  # if found, register kept location
  if not postSchemaAdd.is_lost:
    if not (kept := mysql_crud.kept.register(db, mysql_model.Kept(post_id=post.id, 
                                                              coordinates=tuple2PointString(postSchemaAdd.kept_coordinates), 
                                                              stronghold_id=postSchemaAdd.stronghold_id))):
      raise HTTPException(status_code=500, detail='Failed to register kept')
  
  # hash tags
  for hashtag in postSchemaAdd.hashtags:
    if not (tag := mysql_crud.hashtag.get(db, hashtag)):
      tag = mysql_crud.hashtag.register(db, hashtag)
    
    if tag_match := mysql_crud.tag_match.register(db, mysql_model.TagMatch(post_id=post.id, tag_name=tag.name)):
      tag = mysql_crud.hashtag.update(db, tag.name)
  
  # photos
  for i in range(len(postSchemaAdd.photos)):
    ext, data = dataURL2Img(postSchemaAdd.photos[i])
    if not (photo := mysql_crud.photo.register(db, mysql_model.Photo(id=postImgName(post.id, i, ext), 
                                                                     post_id=post.id, 
                                                                     extension=ext, 
                                                                     data=data))):
      pass
    
  # personal_idlist
  if postSchemaAdd.personal_idlist:
    for name, value in postSchemaAdd.personal_idlist.items():
      if not (identity := mysql_crud.identity.register(db, mysql_model.Identity(post_id=post.id, 
                                                                                name=name,
                                                                                value=value))):
        pass
  
  postView = mysql_crud.view.get(db, post.id)
  return point2TupleStructure(postView)


@router.put('/{post_id}')
async def updatePost(post_id: str,
                     postSchemaUpdate: mysql_schema.PostSchemaUpdate,
                     user: mysql_model.User = Depends(loadUser),
                     db: Session = Depends(mysql_db.getDB)):
  # not implemented perfectly
  if not (post := mysql_crud.post.get(db, post_id)):
    raise HTTPException(status_code=404, detail='Post not found')
  
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='Unauthorized user')
  
  if not (post := mysql_crud.post.update(db, post_id, postSchemaUpdate)):
    raise HTTPException(status_code=500, detail='Failed to update post')
  
  return post


@router.delete('/{post_id}')
async def deletePost(post_id: str,
                     user: mysql_model.User = Depends(loadUser),
                     db: Session = Depends(mysql_db.getDB)):
  if not (post := mysql_crud.post.get(db, post_id)):
    raise HTTPException(status_code=404, detail='Post not found')
  
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='Unauthorized user')
  
  if not mysql_crud.post.delete(db, post_id):
    raise HTTPException(status_code=500, detail='Failed to delete post')
  
  return Response(status_code=204)


router.include_router(post_func.router)
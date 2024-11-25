from fastapi import APIRouter, Response, HTTPException, Depends, Query, Form, File, UploadFile

from sqlalchemy.orm import Session

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from modules.utils import img2DataURL

from routers.dependencies import loadUser


router = APIRouter(prefix='/image', tags=['Post-Image'])

@router.get('/')
async def getPhotos(post_id: str,
                    db: Session = Depends(mysql_db.getDB)):
  images = mysql_crud.photo.getAll(db, post_id)
  for i, image in enumerate(images):
    img = mysql_crud.photo.get(db, image)
    images[i] = img2DataURL(img.extension, img.data)
  return images

@router.post('/')
async def registerPhoto(post_id: str,
                        image: UploadFile = File(...),
                        user: mysql_model.User = Depends(loadUser),
                        db: Session = Depends(mysql_db.getDB)):
  if not (post := mysql_crud.post.get(db, post_id)):
    raise HTTPException(status_code=404, detail='Post not found')
  
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='Permission denied')
  
  try:
    extension = image.filename.split('.')[-1]
  except:
    raise HTTPException(status_code=400, detail='Invalid image')
  
  last_photo = mysql_crud.photo.getAll(db, post_id)
  if last_photo:
    last_photo = last_photo[-1]
    photo_id = str(int(last_photo[37:]) + 1)
    photo_id = f"{post_id}_{photo_id}"
  else:
    photo_id = f"{post_id}_{1}"
  
  if not (photo := mysql_crud.photo.register(db, mysql_model.Photo(id=photo_id, post_id=post_id, extension=extension, data=image.file.read()))):
    raise HTTPException(status_code=400, detail='Failed to register photo')
  
  return photo

@router.delete('/{photo_id}')
async def deletePhoto(post_id: str,
                      photo_id: str,
                      user: mysql_model.User = Depends(loadUser),
                      db: Session = Depends(mysql_db.getDB)):
  if not (post := mysql_crud.post.get(db, post_id)):
    raise HTTPException(status_code=404, detail='Post not found')
  
  if post.user_id != user.id:
    raise HTTPException(status_code=403, detail='Permission denied')
  
  if not mysql_crud.photo.delete(db, photo_id):
    raise HTTPException(status_code=404, detail='Photo not found')
  
  return Response(status_code=204)
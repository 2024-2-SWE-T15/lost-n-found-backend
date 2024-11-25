from fastapi import APIRouter, Response, HTTPException, Depends, Query, Form

from sqlalchemy.orm import Session

from modules.utils import thumbnail, img2DataURL

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from tasks.recommand import related

from routers.dependencies import loadUser


router = APIRouter(prefix='/recommand', tags=['Post-Recommandation'])

@router.get('/')
async def getRecommand(post_id: str,
                       db: Session = Depends(mysql_db.getDB)):
  post = mysql_crud.post.get(db, post_id)
  if not post:
    raise HTTPException(status_code=404, detail='Post not found')
  
  related_lost, related_found = await related(db, post.id)
  related_dict = {}
  related_dict['lost'] = []
  related_dict['found'] = []
  for key, value in related_lost['post_id'].items():
    photo = mysql_crud.photo.getAll(db, value)
    related_dict['lost'].append({
      'id': value,
      'title': related_lost['title'][key],
      'tags': related_lost['tag_name'][key],
      'thumbnail': img2DataURL('png', thumbnail(mysql_crud.photo.get(db, photo[0]).data)) if photo else None,
    })
  for key, value in related_found['post_id']:
    photo = mysql_crud.photo.getAll(db, value)
    related_dict['found'].append({
      'id': value,
      'title': related_found['title'][key],
      'tags': related_found['tag_name'][key],
      'thumbnail': img2DataURL('png', thumbnail(mysql_crud.photo.get(db, photo[0]).data)) if photo else None,
    })
  
  return related_dict
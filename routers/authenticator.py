import os
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from modules import oauth2
from modules.utils import tokenReform

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from db.sqlite import database as sqlite_db
from db.sqlite import crud as sqlite_crud

from .dependencies import oauth, loadUser, verifyToken

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.get('/login/{provider}')
async def login(request: Request, provider: str):
  oauth_client = oauth.create_client(provider)
  return await oauth_client.authorize_redirect(request, (await oauth_client.load_server_metadata())['redirect_uri'])


@router.get('/{provider}/callback')
async def authCallback(request: Request, provider: str,
                       db: Session = Depends(mysql_db.getDB)):
  oauth_client = oauth.create_client(provider)
  try:
    token = await oauth_client.authorize_access_token(request)
  except Exception as e:
    raise HTTPException(status_code=400, detail='Unauthorized access')
  
  try:
    userinfo = await oauth_client.userinfo(token=token)
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

  if not (user := mysql_crud.user.get(db, mysql_model.User(id=oauth2.getOpenID(userinfo, provider), platform=provider))):
    user = mysql_crud.user.register(db, mysql_model.User(id=oauth2.getOpenID(userinfo, provider), platform=provider, 
                                                            nickname=oauth2.getNickname(userinfo, provider), 
                                                            profile_image_url=oauth2.getProfileImageURL(userinfo, provider)))
  else:
    user = mysql_crud.user.update(db, mysql_model.User(id=oauth2.getOpenID(userinfo, provider), platform=provider,
                                                      profile_image_url=oauth2.getProfileImageURL(userinfo, provider)))
  if not user:
    raise HTTPException(status_code=500, detail='Failed to register user')
  
  return tokenReform(token, provider)


@router.put('/')
async def updateUserInfo(userSchemaUpdate: mysql_schema.UserSchemaUpdate,
                         db: Session = Depends(mysql_db.getDB),
                         user: mysql_model.User = Depends(loadUser)):
  user = mysql_crud.user.update(db, mysql_model.User(user.id, userSchemaUpdate.nickname, userSchemaUpdate.profile_image_url))
  if not user:
    raise HTTPException(status_code=500, detail='Failed to update user')
  return user


@router.delete("/")
async def logout(request: Request, 
                 db: Session = Depends(sqlite_db.getDB),
                 user: mysql_model.User = Depends(loadUser)):
  if not sqlite_crud.addInvalidAccessToken(db, request.headers.get('Authorization').split(' ', maxsplit=2)[1]):
    raise HTTPException(status_code=500, detail='Failed to logout')
  
  return Response(status_code=204)


@router.get("/verification")
async def verifyToken(user: mysql_model.User = Depends(verifyToken)):
  return Response(status_code=200)


@router.get("/token")
async def refreshToken(request: Request):
  refresh_token = request.headers.get('Refresh-Token')
  if not refresh_token:
    raise HTTPException(status_code=400, detail='Refresh-Token not found')
  
  try:
    provider, refresh_token = refresh_token.split(' ', maxsplit=2)
  except ValueError:
    raise HTTPException(status_code=400, detail='Invalid Refresh-Token')
  
  oauth_client = oauth.create_client(provider)
  return tokenReform(await oauth_client.fetch_access_token(refresh_token=refresh_token, grant_type='refresh_token',), provider)
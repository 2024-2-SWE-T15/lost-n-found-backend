import os
from dotenv import load_dotenv

from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from modules import oauth2

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from db.sqlite import database as sqlite_db
from db.sqlite import crud as sqlite_crud

from .dependencies import oauth, getCurrentUser

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.get('/login/{provider}')
async def login(request: Request, provider: str):
  oauth_client = oauth.create_client(provider)
  return await oauth_client.authorize_redirect(request, (await oauth_client.load_server_metadata())['redirect_uri'])


@router.get('/{provider}/callback')
async def authCallback(request: Request, provider: str,
                       db: Session = Depends(mysql_db.getDB)):
  oauth_client = oauth.create_client(provider)
  token = await oauth_client.authorize_access_token(request)
  
  try:
    userinfo = await oauth_client.userinfo(token=token)
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

  if not (user := mysql_crud.getUser(db, mysql_model.User(id=oauth2.getOpenID(userinfo, provider), platform=provider))):
    user = mysql_crud.registerUser(db, mysql_model.User(id=oauth2.getOpenID(userinfo, provider), platform=provider, 
                                                            nickname=oauth2.getNickname(userinfo, provider), 
                                                            profile_image_url=oauth2.getProfileImageURL(userinfo, provider)))
  else:
    user = mysql_crud.updateUser(db, mysql_model.User(id=oauth2.getOpenID(userinfo, provider), platform=provider,
                                                      profile_image_url=oauth2.getProfileImageURL(userinfo, provider)))
  if not user:
    raise HTTPException(status_code=500, detail='Failed to register user')
  
  token = {'access_token': f"{provider} {token['access_token']}",
          'refresh_token': token['refresh_token'],
          'token_type': 'Bearer'}
  return token


@router.put('/')
async def updateUserInfo(userSchemaUpdate: mysql_schema.UserSchemaUpdate,
                         db: Session = Depends(mysql_db.getDB),
                         userID: str = Depends(getCurrentUser)):
  user = mysql_crud.updateUser(db, mysql_model.User(userID, userSchemaUpdate.nickname, userSchemaUpdate.profile_image_url))
  if not user:
    raise HTTPException(status_code=500, detail='Failed to update user')
  return user


@router.delete("/")
async def logout(request: Request, 
                 db: Session = Depends(sqlite_db.getDB),
                 userID: str = Depends(getCurrentUser)):
  if not sqlite_crud.addInvalidAccessToken(db, request.headers.get('Authorization').split(' ', maxsplit=2)[1]):
    raise HTTPException(status_code=500, detail='Failed to logout')
  
  return Response(status_code=204)


@router.get("/token")
async def token(userID: str = Depends(getCurrentUser)):
  return userID
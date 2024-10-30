import os

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

from .dependencies import oauth, loadUser, verifyToken, refreshToken

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.get('/login/{provider}')
async def login(request: Request, provider: str):
  if request.cookies.get(f'refresh-token-{provider}'):
    return RedirectResponse(url=f'/auth/{provider}/callback')
  oauth_client = oauth.create_client(provider)
  return await oauth_client.authorize_redirect(request, (await oauth_client.load_server_metadata())['redirect_uri'])


@router.get('/{provider}/callback')
async def authCallback(request: Request, provider: str,
                       db: Session = Depends(mysql_db.getDB)):
  oauth_client = oauth.create_client(provider)
  if request.cookies.get(f'refresh-token-{provider}'):
    token = await refreshToken(request, provider)
  else:
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
  
  token = tokenReform(token, provider)
  response = Response(status_code=200, content="Login success")
  
  response.set_cookie(key="access-token", value=token['access_token'], httponly=True, secure=True, samesite="None")
  if 'refresh_token' in token:
    response.set_cookie(key=f"refresh-token-{provider}", value=token['refresh_token'], httponly=True, secure=True, samesite="None")
  
  return response


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
  response = Response(status_code=204)
  response.delete_cookie('access-token')
  return response


@router.get("/verification")
async def verifyToken(user: mysql_model.User = Depends(verifyToken)):
  return Response(status_code=200)

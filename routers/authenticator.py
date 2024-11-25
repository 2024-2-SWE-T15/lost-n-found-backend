import os
import uuid
import base64
import ast

from fastapi import APIRouter, Depends, Request, Response, HTTPException, Query
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from modules import oauth2
from modules.utils import tokenReform, dataURL2Img, img2DataURL

from db.mysql import database as mysql_db
from db.mysql import model as mysql_model
from db.mysql import crud as mysql_crud
from db.mysql import schema as mysql_schema

from db.sqlite import database as sqlite_db
from db.sqlite import crud as sqlite_crud
from db.sqlite import model as sqlite_model

from .dependencies import oauth, loadUser, verifyToken, refreshToken, unlink

router = APIRouter(prefix='/auth', tags=['Authentication'])

def createCSRFState(db: Session, redirect_url: str, provider: str) -> str:
  while (csrf_token := str(uuid.uuid4())) and sqlite_crud.getCSRFToken(db, redirect_url):
    pass
  
  if not sqlite_crud.addCSRFToken(db, csrf_token, redirect_url):
    raise HTTPException(status_code=500, detail='Failed to create CSRF state')
  
  state_data = {
    'csrf_token': csrf_token,
    'provider': provider
  }
  return base64.urlsafe_b64encode(str(state_data).encode()).decode()
  
def verifyCSRFState(db: Session, state: str, provider: str) -> sqlite_model.CSRFToken:
  try:
    state_data = ast.literal_eval(base64.urlsafe_b64decode(state).decode())
    if not state_data['csrf_token'] or not state_data['provider']:
      raise HTTPException(status_code=400, detail='Invalid CSRF state')
    
    if state_data['provider'] != provider:
      raise HTTPException(status_code=400, detail='Invalid CSRF state')
    
    if not (csrf := sqlite_crud.getCSRFToken(db, state_data['csrf_token'])):
      raise HTTPException(status_code=400, detail='Invalid CSRF state')
    
    return csrf
  except Exception as e:
    raise HTTPException(status_code=400, detail='Invalid CSRF state')

@router.get('/login/{provider}')
async def login(request: Request, provider: str,
                redirect_url: str = Query(...),
                sqlite_db: Session = Depends(sqlite_db.getDB)):
  request.session['oauth_state'] = createCSRFState(sqlite_db, redirect_url, provider)
  
  oauth_client = oauth.create_client(provider)
  return await oauth_client.authorize_redirect(request, (await oauth_client.load_server_metadata())['redirect_uri'])


@router.get('/{provider}/callback')
async def authCallback(request: Request, provider: str,
                       db: Session = Depends(mysql_db.getDB),
                       sqlite_db: Session = Depends(sqlite_db.getDB)):
  if not (state := request.session.pop('oauth_state', None)):
    raise HTTPException(status_code=400, detail='Invalid state')
  if not (csrf_state := verifyCSRFState(sqlite_db, state, provider)):
    raise HTTPException(status_code=400, detail='Invalid state')
  
  oauth_client = oauth.create_client(provider)
  if request.session.get(f'refresh-token-{provider}'):
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
                                                            profile_image_url=oauth2.getProfileImageURL(userinfo, provider),
                                                            email=oauth2.getEmailAddress(userinfo, provider)))
  else:
    user = mysql_crud.user.update(db, mysql_model.User(id=oauth2.getOpenID(userinfo, provider), platform=provider,
                                                      profile_image_url=oauth2.getProfileImageURL(userinfo, provider)))
  if not user:
    raise HTTPException(status_code=500, detail='Failed to register user')
  
  token = tokenReform(token, provider)
  # response = Response(status_code=200, content="Login success")
  response = RedirectResponse(url=csrf_state.redirect_url)
  
  # response.set_cookie(key="access-token", value=token['access_token'], httponly=True, secure=True, samesite="None")
  request.session['access-token'] = token['access_token']
  if 'refresh_token' in token:
    # response.set_cookie(key=f"refresh-token-{provider}", value=token['refresh_token'], httponly=True, secure=True, samesite="None")
    request.session[f"refresh-token-{provider}"] = token['refresh_token']
  
  
  try:
    sqlite_crud.removeCSRFToken(sqlite_db, csrf_state.csrf_token)
  except Exception as e:
    pass
  
  return response


@router.get('/userinfo')
async def getUserInfo(db: Session = Depends(mysql_db.getDB),
                      user: mysql_model.User = Depends(loadUser)):
  if user.profile_image_url == '-':
    profile = mysql_crud.profile.get(db, user.id)
    user.profile_image_url = img2DataURL(profile.extension, profile.data)
  return user


@router.put('/')
async def updateUserInfo(userSchemaUpdate: mysql_schema.UserSchemaUpdate,
                         db: Session = Depends(mysql_db.getDB),
                         user: mysql_model.User = Depends(loadUser)):
  if userSchemaUpdate.profile_image_url:
    tmp = dataURL2Img(userSchemaUpdate.profile_image_url)
    profile = mysql_crud.profile.update(db, mysql_model.Profile(user_id=user.id, data=tmp[1], extension=tmp[0]))
    if not profile:
      raise HTTPException(status_code=500, detail='Failed to update profile image')
    
    user = mysql_crud.user.update(db, mysql_model.User(id=user.id, 
                                                      nickname=userSchemaUpdate.nickname,
                                                      platform=user.platform,
                                                      profile_image_url="-",
                                                      email=userSchemaUpdate.email))
    
  else:
    user = mysql_crud.user.update(db, mysql_model.User(id=user.id, 
                                                      nickname=userSchemaUpdate.nickname,
                                                      platform=user.platform,
                                                      email=userSchemaUpdate.email))
  if not user:
    raise HTTPException(status_code=500, detail='Failed to update user')
  
  return user


@router.delete("/")
async def logout(request: Request, 
                 db: Session = Depends(sqlite_db.getDB),
                 user: mysql_model.User = Depends(loadUser)):
  response = Response(status_code=204)
  if request.session.get('access-token'):
    del request.session['access-token']
  if request.session.get(f'refresh-token-{user.platform}'):
    del request.session[f'refresh-token-{user.platform}']
  # response.delete_cookie('access-token')
  # response.delete_cookie(f'refresh-token-{user.platform}')
  return response

@router.delete("/withdrawal")
async def withdrawal(request: Request,
                     db: Session = Depends(mysql_db.getDB),
                     user: mysql_model.User = Depends(loadUser)):
  r = await unlink(request)
  if r and r.get('result') != 'success':
    raise HTTPException(status_code=500, detail='Failed to unlink user')
  
  if not mysql_crud.user.delete(db, user):
    raise HTTPException(status_code=500, detail='Failed to delete user')
  
  response = Response(status_code=204)
  if request.session.get('access-token'):
    del request.session['access-token']
  if request.session.get(f'refresh-token-{user.platform}'):
    del request.session[f'refresh-token-{user.platform}']
  # response.delete_cookie('access-token')
  # response.delete_cookie(f'refresh-token-{user.platform}')
  return response


@router.get("/verification")
async def verifyToken(user: mysql_model.User = Depends(verifyToken)):
  return Response(status_code=200)

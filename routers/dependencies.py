import os
import httpx
from datetime import timedelta

from sqlalchemy.orm import Session

from fastapi import Request, HTTPException, Depends
from fastapi_login import LoginManager
from authlib.integrations.starlette_client import OAuth

from google.auth.transport import requests as google_requests
from google.oauth2.id_token import verify_oauth2_token

from modules import oauth2
from modules.utils import tokenReform

from db.mysql.database import SessionLocal, getDB
from db.mysql.model import User

PROTOCOL = os.getenv('PROTOCOL')
HOST = os.getenv('HOST')
# PORT = int(os.getenv('PORT'))

platforms = ['google', 'kakao', 'naver']

oauth = OAuth()

# OAuth Config
oauth.register(
  name='google',
  client_id=os.getenv('GOOGLE_CLIENT_ID'),
  client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
  authorize_url='https://accounts.google.com/o/oauth2/auth',
  authorize_params={
    'access_type': 'offline',
    # 'prompt': 'consent', # authorization prompt : request user consent every time, if not set, it requires refresh token
  },
  access_token_url='https://accounts.google.com/o/oauth2/token',
  access_token_params={
    'access_type': 'offline',
  },
  refresh_token_url=None,
  # redirect_uri=f'{PROTOCOL}://{HOST}:{PORT}/auth/google/callback',
  redirect_uri=f'{PROTOCOL}://{HOST}/auth/google/callback',
  userinfo_endpoint='https://www.googleapis.com/oauth2/v3/userinfo',
  jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
  client_kwargs={'scope': 'openid email profile'}
)

oauth.register(
  name='kakao',
  client_id=os.getenv('KAKAO_REST_API_KEY'),
  authorize_url='https://kauth.kakao.com/oauth/authorize',
  authorize_params=None,
  access_token_url='https://kauth.kakao.com/oauth/token',
  access_token_params={
    # 'prompt': 'select_account',
  },
  refresh_token_url=None,
  # redirect_uri=f'{PROTOCOL}://{HOST}:{PORT}/auth/kakao/callback',
  redirect_uri=f'{PROTOCOL}://{HOST}/auth/kakao/callback',
  userinfo_endpoint='https://kapi.kakao.com/v2/user/me',
  client_kwargs={'scope': 'openid, profile_nickname, profile_image'}
)

oauth.register(
  name='naver',
  client_id=os.getenv('NAVER_CLIENT_ID'),
  client_secret=os.getenv('NAVER_CLIENT_SECRET'),
  authorize_url='https://nid.naver.com/oauth2.0/authorize',
  authorize_params=None,
  access_token_url='https://nid.naver.com/oauth2.0/token',
  access_token_params=None,
  refresh_token_url=None,
  # redirect_uri=f'{PROTOCOL}://{HOST}:{PORT}/auth/naver/callback',
  redirect_uri=f'{PROTOCOL}://{HOST}/auth/naver/callback',
  userinfo_endpoint='https://openapi.naver.com/v1/nid/me',
  client_kwargs={'scope': 'profile'}
)
 

async def verifyToken(request: Request):
  if not (token := request.cookies.get('access-token')):
    raise HTTPException(status_code=401, detail='Invalid Credentials')
  
  provider, access_token = token.split(' ')
  token = {'access_token': access_token, 
           'token_type': 'Bearer'}
  
  oauth_client = oauth.create_client(provider)
  try:
    userinfo = await oauth_client.userinfo(token=token)
  except httpx.HTTPStatusError as e:
    try:
      userinfo = await oauth_client.userinfo(token=await refreshToken(request, provider))
    except httpx.HTTPStatusError as e:
      raise oauth2.convertHTTPException(e, provider)
  
  try:
    return str(oauth2.getOpenID(userinfo, provider)), provider
  except HTTPException as e:
    raise e
  except Exception as e:
    raise e


async def getCurrentUser(token_info: tuple[str, str] = Depends(verifyToken),
                         db: Session = Depends(getDB)):
  (id, provider) = token_info
  
  if not db:
    with SessionLocal() as db:
      return db.query(User).filter(User.id == str(id), User.platform == provider).first()
  return db.query(User).filter(User.id == id, User.platform == provider).first()

async def loadUser(user: User = Depends(getCurrentUser)):
  if not user:
    raise HTTPException(status_code=401, detail='Unauthorized access')
  return user


async def refreshToken(request: Request, provider: str):
  if not (refresh_token := request.cookies.get(f'refresh-token-{provider}')):
    return None

  oauth_client = oauth.create_client(provider)
  return await oauth_client.fetch_access_token(refresh_token=refresh_token, grant_type='refresh_token',)

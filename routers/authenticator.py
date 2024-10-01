import os
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse

from google.auth.transport import requests as google_requests
from google.oauth2.id_token import verify_oauth2_token

from .dependencies import getCurrentUser

PROTOCOL = os.getenv('PROTOCOL')
HOST = os.getenv('HOST')
# PORT = int(os.getenv('PORT'))

router = APIRouter(prefix='/auth', tags=['Authentication'])

oauth = OAuth()

# OAuth Config
oauth.register(
  name='google',
  client_id=os.getenv('GOOGLE_CLIENT_ID'),
  client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
  authorize_url='https://accounts.google.com/o/oauth2/auth',
  authorize_params=None,
  access_token_url='https://accounts.google.com/o/oauth2/token',
  access_token_params=None,
  refresh_token_url=None,
  # redirect_uri=f'{PROTOCOL}://{HOST}:{PORT}/auth/google/callback',
  redirect_uri=f'{PROTOCOL}://{HOST}/auth/google/callback',
  userinfo_endpoint='https://www.googleapis.com/oauth2/v3/userinfo',
  jwks_uri='https://www.googleapis.com/oauth2/v3/certs',
  client_kwargs={'scope': 'openid email profile'}
)

# oauth.register(
#   name='kakao',
#   client_id='KAKAO_CLIENT_ID',
#   client_secret='KAKAO_CLIENT_SECRET',
#   authorize_url='https://kauth.kakao.com/oauth/authorize',
#   authorize_params=None,
#   access_token_url='https://kauth.kakao.com/oauth/token',
#   access_token_params=None,
#   refresh_token_url=None,
#   # redirect_uri=f'{PROTOCOL}://{HOST}:{PORT}/auth/kakao/callback',
#   redirect_uri=f'{PROTOCOL}://{HOST}/auth/kakao/callback',
#   client_kwargs={'scope': 'profile_nickname, profile_image'}
# )

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

# @router.post('/')
# async def generateToken(request: Request)


@router.get('/login/{provider}')
async def login(request: Request, provider: str):
  oauth_client = oauth.create_client(provider)
  print(oauth_client.__dict__)
  # redirect_uri = f'{PROTOCOL}://{HOST}:{PORT}/auth/{provider}/callback'
  redirect_uri = f'{PROTOCOL}://{HOST}/auth/{provider}/callback'
  return await oauth_client.authorize_redirect(request, redirect_uri)
  # return await oauth_client.authorize_redirect(request, f'{PROTOCOL}://{HOST}')


@router.get('/{provider}/callback')
async def auth_callback(request: Request, provider: str):
  oauth_client = oauth.create_client(provider)
  print(oauth_client.__dict__)
  print(oauth.load_config('naver', 'userinfo_url'))
  token = await oauth_client.authorize_access_token(request)
  print(token)
  if provider == 'google':
    # user_info = await oauth_client.parse_id_token(token, nonce=token['userinfo']['nonce'])
    user_info = await oauth_client.userinfo(token=token)
  else:
    user_info = await oauth_client.userinfo(token=token)
  # userInfo = await oauth_client.get('userinfo_endpoint', token=token)
  # Here you can create the user in MySQL if not exist
  
  return user_info

@router.get("/token")
async def token(request: Request, userID: str = Depends(getCurrentUser)):
  oauth_client = oauth.create_client('google')
  print(userID)
  return {"access_token": userID}
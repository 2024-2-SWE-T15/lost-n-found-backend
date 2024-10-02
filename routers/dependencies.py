import os
import httpx
from datetime import timedelta
from dotenv import load_dotenv

from fastapi import Request, HTTPException, Depends
from fastapi_login import LoginManager
from authlib.integrations.starlette_client import OAuth

from google.auth.transport import requests as google_requests
from google.oauth2.id_token import verify_oauth2_token

from modules import oauth2

load_dotenv('config/.env')

PROTOCOL = os.getenv('PROTOCOL')
HOST = os.getenv('HOST')
# PORT = int(os.getenv('PORT'))

oauth = OAuth()

# OAuth Config
oauth.register(
  name='google',
  client_id=os.getenv('GOOGLE_CLIENT_ID'),
  client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
  authorize_url='https://accounts.google.com/o/oauth2/auth',
  authorize_params={
    'access_type': 'offline',
    'prompt': 'consent',
  },
  access_token_url='https://accounts.google.com/o/oauth2/token',
  access_token_params=None,
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
    'prompt': 'select_account',
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
  if not (token := request.headers.get('Authorization')):
    raise HTTPException(status_code=401, detail='Invalid Credentials')
  # refresh_token = request.headers.get('Refresh-Token')
  token_type, provider, access_token = token.split(' ')
  token = {'access_token': access_token, 
          #  'refresh_token': refresh_token, 
           'token_type': token_type}
  
  oauth_client = oauth.create_client(provider)
  try:
    return await oauth_client.userinfo(token=token), provider
  except HTTPException as e:
    raise e
  except httpx.HTTPStatusError as e:
    print(e.response.json())
    raise oauth2.convertHTTPException(e, provider)
  except Exception as e:
    raise e


async def getCurrentUser(token_info = Depends(verifyToken)):
  (idinfo, provider) = token_info
  return oauth2.getOpenID(idinfo, provider), provider
import os
import pytz
import jwt
import json
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler

from sqlalchemy.orm import Session

import uvicorn
from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from db.sqlite import database as sqlite_db
from db.sqlite import crud as sqlite_crud

from modules.utils import tokenReform

from tasks import alert, cache, update

from routers.dependencies import verifyToken, refreshToken
from routers import authenticator, postboard, coordinates

load_dotenv("config/.env")

# scheduler
krTZ = pytz.timezone('Asia/Seoul')
scheduler = BackgroundScheduler(timezone=krTZ)
scheduler.add_job(cache.clearTokenMemories, 'interval', minutes=5, timezone=krTZ)
scheduler.add_job(cache.clearCSRFToken, 'interval', minutes=3, timezone=krTZ)
# scheduler.add_job(update.updateMatchRank, 'interval', minutes=30, timezone=krTZ)

def start():
  scheduler.start()

def shutdown():
  scheduler.shutdown()

@asynccontextmanager
async def lifespan(app: FastAPI):
  start()
  
  yield
  
  shutdown()
  

app = FastAPI(lifespan=lifespan)

# middlewares
# @app.middleware("http")
# async def checkAccessToken(request: Request, call_next):
#   flag = True
#   if request.headers.get('Authorization'):
#     token = request.headers.get('Authorization')
#     _, access_token = token.split(' ', maxsplit=1)
#     db = next(sqlite_db.getDB())
#     if sqlite_crud.getInvalidAccessToken(db, access_token):
#       try:
#         del request.headers['Authorization']
#       except KeyError:
#         pass
#     else:
#       flag = False
      
#   if request.headers.get('Refresh-Token') and flag:
#     try:
#       del request.headers['Refresh-Token']
#     except KeyError:
#       pass
  
#   response = await call_next(request)
#   return response

@app.middleware("http")
async def checkAccessToken(request: Request, call_next):
  access_token = None
  if request.cookies.get('access-token'):
    token = request.cookies.get('access-token')
    provider, _ = token.split(' ')
    refresh_token = request.cookies.get(f'refresh-token-{provider}')
    if cache.getTokenMemory(refresh_token):
      return await call_next(request)
    
    if not (token := await refreshToken(request, provider)):
      response = Response(status_code=401, content='detail: Invalid Credentials')
      response.delete_cookie('access-token')
      response.delete_cookie(f'refresh-token-{provider}')
      return response
    
    access_token = tokenReform(token, provider)['access_token']
    request.cookies['access-token'] = access_token
      
  response = await call_next(request)
  if access_token:
    response.set_cookie(key="access-token", value=access_token, httponly=True, secure=True, samesite="None")
    cache.addTokenMemory(refresh_token)
  
  return response


app.add_middleware(SessionMiddleware, secret_key=os.getenv('SECRET'))
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

# routers
app.include_router(authenticator.router)
app.include_router(coordinates.router)
app.include_router(postboard.router)


# root route
@app.get("/")
async def root():
  return {"message": "Hello World"}

@app.get("/test")
async def test():
  # if alert.send_alert("ekfzkr@kakao.com", "주현", [("03160742-7b9a-4266-ab12-ac7163d75df2", "잃어버린 린스, 어디에 있을까요? 도움이 필요해요!", "2024-11-14 03:01:57")]):
  #   return Response(status_code=204)
  return Response(status_code=400)


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT')))
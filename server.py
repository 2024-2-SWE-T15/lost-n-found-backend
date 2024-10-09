import os
import pytz
import jwt
import json
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler

from sqlalchemy.orm import Session

import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from db.sqlite import database as sqlite_db
from db.sqlite import crud as sqlite_crud

from tasks import clear, update

from routers.dependencies import getCurrentUser
from routers import authenticator, postboard, coordinates

load_dotenv("config/.env")

# scheduler
krTZ = pytz.timezone('Asia/Seoul')
scheduler = BackgroundScheduler(timezone=krTZ)
scheduler.add_job(clear.clearForbiddenToken, 'interval', minutes=5, timezone=krTZ)
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
@app.middleware("http")
async def checkAccessToken(request: Request, call_next):
  flag = True
  if request.headers.get('Authorization'):
    token = request.headers.get('Authorization')
    _, access_token = token.split(' ', maxsplit=1)
    db = next(sqlite_db.getDB())
    if sqlite_crud.getInvalidAccessToken(db, access_token):
      try:
        del request.headers['Authorization']
      except KeyError:
        pass
    else:
      flag = False
      
  if request.headers.get('Refresh-Token') and flag:
    try:
      del request.headers['Refresh-Token']
    except KeyError:
      pass
  
  response = await call_next(request)
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


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, host='0.0.0.0', port=int(os.getenv('PORT')))
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from db.sqlite import database as sqlite_db
from db.sqlite import model as sqlite_model
from db.sqlite import crud as sqlite_crud

def addTokenMemory(refresh_token: str):
  SessionLocal = sqlite_db.initDB()
  db: Session = SessionLocal()
  try:
    sqlite_crud.addRefreshedToken(db, refresh_token)
  finally:
    db.close()

def getTokenMemory(refresh_token: str):
  SessionLocal = sqlite_db.initDB()
  db: Session = SessionLocal()
  try:
    token_memory = sqlite_crud.getRefreshedToken(db, refresh_token)
    return token_memory
  finally:
    db.close()



def clearTokenMemories():
  SessionLocal = sqlite_db.initDB()
  db: Session = SessionLocal()
  try:
    sqlite_crud.clearRefreshedToken(db)
  finally:
    db.close()
  

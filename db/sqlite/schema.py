from fastapi import UploadFile, File, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# DB Models
class InvalidTokenSchema(BaseModel):
  access_token: str
  create_time: datetime
  
  class Config:
    from_attributes = True
    
from fastapi import UploadFile, File, Query
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# DB Models
class RefreshedTokenSchema(BaseModel):
  refresh_token: str
  create_time: datetime
  
  class Config:
    from_attributes = True

class CSRFTokenSchema(BaseModel):
  csrf_token: str
  redirect_url: str
  create_time: datetime
  
  class Config:
    from_attributes = True
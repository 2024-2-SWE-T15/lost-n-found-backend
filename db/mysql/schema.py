from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# DB Models
class UserSchema(BaseModel):
  id: str
  platform: str
  nickname: str
  profile_image_url: Optional[str]
  create_time: datetime
  update_time: Optional[datetime]
  
  class Config:
    from_attributes = True

# User Schema
class UserSchemaAdd(BaseModel):
  id: str
  platform: str
  nickname: str
  profile_image_url: Optional[str]

class UserSchemaGet(BaseModel):
  id: str
  platform: str

class UserSchemaUpdate(BaseModel):
  nickname: Optional[str]
  profile_image_url: Optional[str]

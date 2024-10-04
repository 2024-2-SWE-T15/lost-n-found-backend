from pydantic import BaseModel
from typing import Optional, Union
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


class PostSchema(BaseModel):
  id: str
  title: str
  user_id: str
  coordinates: tuple
  description: str
  create_time: datetime
  update_time: Optional[datetime]
  valid: bool
  is_lost: bool
  match_rank: int
  
  class Config:
    from_attributes = True


class HashtagSchema(BaseModel):
  name: str
  last_access: datetime
  
  class Config:
    from_attributes = True


class StrongholdSchema(BaseModel):
  id: int
  name: str
  coordinates: tuple
  description: str
  
  class Config:
    from_attributes = True
    
    
class PhotoSchema(BaseModel):
  id: str
  post_id: str
  extension: str
  data: bytes
  
  class Config:
    from_attributes = True


class IdentitySchema(BaseModel):
  post_id: str
  name: str
  value: str
  
  class Config:
    from_attributes = True


class TagMatchSchema(BaseModel):
  post_id: str
  tag_name: str
  
  class Config:
    from_attributes = True


class KeptSchema(BaseModel):
  post_id: str
  coordinates: Optional[tuple[Optional[float], Optional[float]]]
  stronghold_id: Optional[int]
  
  class Config:
    from_attributes = True


# View Schema
class FoundViewSchema(BaseModel):
  id: str
  title: str
  user_id: str
  coordinates: tuple
  description: str
  create_time: datetime
  update_time: Optional[datetime]
  valid: bool
  is_lost: bool
  kept_coordinates: tuple
  stronghold_id: Optional[int]
  
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


# Post Schema
class PostSchemaAdd(BaseModel):
  title: str
  coordinates: tuple[float, float]
  kept_coordinates: Optional[tuple[Optional[float], Optional[float]]]
  stronghold_id: Optional[int]
  hashtags: list[str]
  description: str
  photos: list[str]
  personal_idlist: Optional[dict[str, str]]
  is_lost: bool

class PostSchemaUpdate(BaseModel):
  title: Optional[str]
  coordinates: Optional[tuple[float, float]]
  kept_coordinates: Optional[tuple[Optional[float], Optional[float]]]
  stronghold_id: Optional[int]
  hashtags: Optional[dict[str, str]]
  description: Optional[str]
  photos: Optional[dict[str, str]]
  personal_idlist: Optional[dict[str, Union[dict[str, str], str]]]
  
class PostSchemaSearch(BaseModel):
  query: Optional[str] = ""
  tags: Optional[list[str]] = []
  coordinates: Optional[tuple[float, float]] = None
  distance: Optional[float] = None
  is_lost: Optional[bool] = None

# HashTag Schema


# Stronghold Schema
class StrongholdSchemaAdd(BaseModel):
  name: str
  coordinates: tuple
  description: str


# Identity Schema
class IdentitySchemaGet(BaseModel):
  post_id: str
  name: str

class IdentitySchemaGetAll(BaseModel):
  post_id: str

# etc
class CoordinateSchema(BaseModel):
  coordinates: tuple
  distance: float
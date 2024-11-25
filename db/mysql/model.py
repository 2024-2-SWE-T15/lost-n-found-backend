import uuid
from sqlalchemy import Column, Integer, Double, String, Boolean, DateTime, ForeignKey, LargeBinary, Index, TupleType
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from shapely.geometry import Point

Base = declarative_base()

# Table
class User(Base):
  __tablename__ = 'users'
  
  id = Column(String, primary_key=True, index=True)
  platform = Column(String, primary_key=True, index=True)
  nickname = Column(String, nullable=False)
  profile_image_url = Column(String, nullable=True)
  create_time = Column(DateTime, nullable=False)
  update_time = Column(DateTime, nullable=True)
  email = Column(String, nullable=True)

  post = relationship('Post', back_populates='user')
  profile = relationship('profile', back_populates='user')

class Post(Base):
  __tablename__ = 'posts'
  
  id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
  title = Column(String, nullable=False)
  user_id = Column(String, ForeignKey('users.id'), nullable=False)
  coordinates = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
  description = Column(String, nullable=False)
  create_time = Column(DateTime, nullable=False)
  update_time = Column(DateTime, nullable=True)
  valid = Column(Boolean, nullable=False, default=True)
  is_lost = Column(Boolean, nullable=False)
  match_rank = Column(Integer, nullable=False)
  
  user = relationship('User', back_populates='post')
  photo = relationship('Photo', back_populates='post')
  identity = relationship('Identity', back_populates='post')
  tag_match = relationship('TagMatch', back_populates='post')
  kept = relationship('Kept', back_populates='post')


class Hashtag(Base):
  __tablename__ = 'hashtags'
  
  name = Column(String, primary_key=True, index=True)
  last_access = Column(DateTime, nullable=False)
  
  tag_match = relationship('TagMatch', back_populates='hashtag')


class Stronghold(Base):
  __tablename__ = 'strongholds'
  
  id = Column(Integer, primary_key=True, index=True)
  name = Column(String, nullable=False)
  coordinates = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
  description = Column(String, nullable=False)
  
  kept = relationship('Kept', back_populates='stronghold')


class Photo(Base):
  __tablename__ = 'photos'
  
  id = Column(String, primary_key=True, index=True)
  post_id = Column(String, ForeignKey('posts.id'), nullable=False)
  extension = Column(String, nullable=False)
  data = Column(LargeBinary, nullable=False)
  
  post = relationship('Post', back_populates='photo')
  

class Identity(Base):
  __tablename__ = 'identities'
  
  post_id = Column(String, ForeignKey('posts.id'), primary_key=True, index=True)
  name = Column(String, primary_key=True, index=True)
  value = Column(String, nullable=False)
  
  post = relationship('Post', back_populates='identity')


class TagMatch(Base):
  __tablename__ = 'tag_matches'
  
  post_id = Column(String, ForeignKey('posts.id'), primary_key=True, index=True)
  tag_name = Column(String, ForeignKey('hashtags.name'), primary_key=True, index=True)
  
  post = relationship('Post', back_populates='tag_match')
  hashtag = relationship('Hashtag', back_populates='tag_match')


class Kept(Base):
  __tablename__ = 'kepts'
  
  post_id = Column(String, ForeignKey('posts.id'), primary_key=True, index=True)
  coordinates = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
  stronghold_id = Column(Integer, ForeignKey('strongholds.id'), nullable=False)
  
  post = relationship('Post', back_populates='kept')
  stronghold = relationship('Stronghold', back_populates='kept')
  

class Profile(Base):
  __tablename__ = 'profiles'
  
  user_id = Column(String, ForeignKey('users.id'), primary_key=True, index=True)
  data = Column(LargeBinary, nullable=True)
  extension = Column(String, nullable=True)
  
  user = relationship('User', back_populates='profile')
  

class FoundView(Base):
  __tablename__ = 'found_view'
  
  id = Column(String, primary_key=True, index=True)
  title = Column(String, nullable=False)
  user_id = Column(String, ForeignKey('users.id'), nullable=False)
  coordinates = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
  description = Column(String, nullable=False)
  create_time = Column(DateTime, nullable=False)
  update_time = Column(DateTime, nullable=True)
  valid = Column(Boolean, nullable=False)
  is_lost = Column(Boolean, nullable=False)
  match_rank = Column(Integer, nullable=False)
  kept_coordinates = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
  stronghold_id = Column(Integer, ForeignKey('strongholds.id'), nullable=False)
  
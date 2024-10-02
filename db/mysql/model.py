from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, LargeBinary, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

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

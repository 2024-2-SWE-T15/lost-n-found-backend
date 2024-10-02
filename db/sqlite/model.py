from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Table
class InvalidToken(Base):
  __tablename__ = 'invalid_tokens'
  access_token = Column(String, primary_key=True, index=True)
  create_time = Column(DateTime, nullable=False, index=True)

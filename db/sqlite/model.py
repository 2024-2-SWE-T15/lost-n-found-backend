from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Table
class RefreshedToken(Base):
  __tablename__ = 'refreshed_tokens'
  refresh_token = Column(String, primary_key=True, index=True)
  create_time = Column(DateTime, nullable=False, index=True)

class CSRFToken(Base):
  __tablename__ = 'csrf_tokens'
  csrf_token = Column(String, primary_key=True, index=True)
  redirect_uri = Column(String, nullable=False)
  create_time = Column(DateTime, nullable=False, index=True)
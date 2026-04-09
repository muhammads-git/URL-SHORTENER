from sqlalchemy import Column, Integer , String, DateTime , ForeignKey ,Interval
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timedelta, timezone


class Url(Base):
   __tablename__ = 'urls'

   id = Column(Integer, primary_key=True)
   longUrl = Column(String)
   shortUrl = Column(String, unique=True)
   clicks = Column(Integer, default=0)
   created_at = Column(DateTime, default=datetime.utcnow)

   # new column
   expires_at = Column(DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(days=30))

   # relationship col
   user_id = Column(Integer, ForeignKey('users.id') ,nullable=True)

   owner = relationship('User', back_populates="urls")

# users
class User(Base):
   __tablename__ = "users"

   id = Column(Integer, primary_key=True, index=True, nullable=False)
   username = Column(String, index=True, nullable=False)
   email = Column(String, index=True, nullable=False)
   password = Column(String, nullable=False)
   created_at = Column(DateTime, default=datetime.utcnow)

   # relationship to urls 
   urls = relationship('Url', back_populates="owner")


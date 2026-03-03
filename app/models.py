from sqlalchemy import Column, Integer , String
from app.database import Base



class Url(Base):
   __tablename__ = 'urls'

   id = Column(Integer, primary_key=True)
   longUrl = Column(String)
   shortUrl = Column(String, unique=True)


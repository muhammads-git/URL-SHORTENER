from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

# load . env
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


# create engine
engine = create_engine(DATABASE_URL)

# sessionmaker // this is a session
SessionLocal = sessionmaker(
   autoflush=False,
   autocommit = False,
   bind=engine
)

Base = declarative_base()

# get_db
def get_db():
   db = SessionLocal()
   try:
      yield db
   finally:
      db.close()   

# url_db = {}

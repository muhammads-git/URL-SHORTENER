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


url_db = {}

from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse,Response
# from pydantic import BaseModel
from app.utils import GenerateTemperoryCode
from app.database import engine, Base, get_db
from app.models import Url, User
from sqlalchemy.orm import Session 
from sqlalchemy import text
from app.auths.auth import hashPassword, checkPassword,ACCESS_TOKEN_EXPIRE_MINUTES,createAccessToken,getTokenExpiration,decodeToken
from app.schemas.schema import UserCreate
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime,timedelta,timezone
from fastapi.middleware.cors import CORSMiddleware
from app.schedular.background_job import startSchedular,shutdownSchedular
import atexit
from app.services.ai_service import generate_slugs
from app.services.scraper_service import get_page_title
from arq import create_pool
from app.lifespan import lifespan
from app.routers.auths import router as auth_router
from app.routers.urls import router as url_router
from app.routers.analytics import router as analytics_router
from app.routers.auths import getCurrentUser

# CONFIGURATIONS 

# set up FASTAPI instance
app = FastAPI(title='URL SHORTENER',lifespan=lifespan)
# connect diff routers
app.include_router(auth_router, prefix='/auth', tags=['auth'])
app.include_router(analytics_router, tags=['analytics'])
app.include_router(url_router, tags=['urls'])  # wildcard always last
# start schedular
schedular = startSchedular()
# shutdown
atexit.register(lambda: shutdownSchedular(schedular))
# Create tables
Base.metadata.create_all(bind=engine)



@app.get('/')
async def hello( request: Request):
    # return templates.TemplateResponse('url.html' ,{'request': request})
    return {'message': 'hello'}
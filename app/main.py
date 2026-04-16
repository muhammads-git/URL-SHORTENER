from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
# from pydantic import BaseModel
from app.utils import GenerateShortCode
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
from app.services.rate_limiting_service import checkRateLimit
from app.services.rate_limiting_service import redis_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')
# get current user
def getCurrentUser(token: str = Depends(oauth2_scheme)):
    username = decodeToken(token)
    if not username:
        raise HTTPException(
            status_code=404,
            detail='Invalid Token or no such user found'
        )
    else:
        return username


# set up FASTAPI instance
app = FastAPI(title='URL SHORTENER')

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


# ________________________REGISTRATIONS ROUTES___________________________#
@app.post('/register')
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # // check if user exists already...
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    # check 
    if existing:
        # check username or email taken
        if existing.username == user_data.username:
            detail = 'Username already taken!'
        else:
            detail = 'Email already taken!'
        raise HTTPException(status_code=404, detail=detail)

    # hash password................
    hashedPassword = hashPassword(user_data.password)

    # create user
    newUser = User(
        username = user_data.username,
        email = user_data.email,
        password = hashedPassword
    )
    # save to db
    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    return {'success': True, 'message':'User created!'}

# Login route
@app.post('/login')
def login(user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # now the OAuth2PasswordRequestForm will automatically handle forms
    user = db.query(User).filter(
        (user_data.username == User.username)
    ).first()

    if not user or not checkPassword(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # create token
    accessToken = createAccessToken(data={'sub':user.password})
   # return access token and its type
    return {'access_token': accessToken, 'token_type': 'bearer'}



#             SHORTENER             #
@app.post('/url_shortener')
def create_short_url(request: Request, long_url: str = Form(...), valid_days : int = Form(30) , db: Session = Depends(get_db), current_user = Depends(getCurrentUser)):
    """
    check rate limit
    if true allow or block request
    """
    user_id = db.query(User.id).filter(User.username == current_user).first()
    # res= db.execute(text("SELECT id from users where username=:username"),{
    #     'username':current_user
    # })
    # user_id = res.fetchone()[0]
    checkRateLimit(request,user_id=user_id, max_req=5, time_window=60)
    
    if not current_user:
        raise HTTPException(status_code=401, detail='No user found, Login first!')
    
    # fetch currect user id from db
    user_id = db.query(User.id).filter(User.username == current_user).first()
    print(user_id)

    
    """ 
        genrate short code, 
        then check if the same code already exists
     """
    short_code = GenerateShortCode()
    
    # Check if code already exists
    while db.query(Url).filter(Url.shortUrl == short_code).first():  # ← shortUrl
        short_code = GenerateShortCode()
    
    # expires at this..
    valid_days = datetime.utcnow() + timedelta(days=valid_days)
    
    # Save to database
    db_url = Url(
        shortUrl=short_code,    # ← shortUrl
        longUrl=long_url,
        expires_at = valid_days,
        user_id=user_id
    )
    db.add(db_url)   # // insertion in db
    db.commit()   # //
    db.refresh(db_url)
    
    return {
        'shortUrl': f'http://localhost:8000/{short_code}',
        'code': short_code,
        'longUrl': long_url

    }

"""
    get/analytics
"""

@app.get('/analytics')
def analytics(request: Request,db: Session = Depends(get_db),current_user = Depends(getCurrentUser)):

    user_id = db.query(User).filter(User.username == current_user).first()
    print(user_id[0])

    if not  user_id:
        raise HTTPException(status_code=404, detail='user_id not found!')
    
    checkRateLimit(request,user_id=user_id, max_req=5, time_window=60)
    
    data = db.query(Url.longUrl,Url.shortUrl,Url.clicks).filter(Url.user_id == user_id).all()
    
    if not data:
        raise HTTPException(detail='No data found!')
    
    # " turn this list of tuples into list of dictionary to access it easily"
    list_data = []
    for d in data:
        list_data.append({

            'long_url':d.longUrl,
            'short_url':d.shortUrl,
            'clicks':d.clicks
        })

    """ find the URL with most clicks"""

    most_clicked = max(list_data, key=lambda x: x['clicks'] )

    return {
    'most_clicked': most_clicked,
    'all_links': [
        {
            'long_url': item['long_url'],
            'short_code': item['short_url'],
            'clicks': item['clicks']
        }
        for item in list_data
    ]
}

@app.get('/{short_code}')
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """  
    apply reddis layer before db:
    if find in reddis redirct to long url:
    if not just go then to db find -> save to reddis now. 
    """
    # reddis layer
    url = redis_client.get(short_code)
    if url:
        return RedirectResponse(url) 
    
    url_entry = db.query(Url).filter(Url.shortUrl == short_code).first()  # ← shortUrl
    
    if not url_entry:
        raise HTTPException(status_code=404, detail='URL not found')
    
    if url_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail='Link has been expired!')
    # calculate expiry of url
    time_remaining = (url_entry.expires_at - datetime.utcnow()).total_seconds()
    
    # save to redis
    key_val = redis_client.setex(f'short_code:{short_code}',int(time_remaining),url_entry.longUrl)
    print(key_val)
    
    """
    now increment in clicks
    to track the url visitors... 
    """
    
    url_entry.clicks += 1
    db.commit() # commit

    url = url_entry.longUrl 

    return RedirectResponse(url)
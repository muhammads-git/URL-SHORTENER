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
from app.services.rate_limiting_service import checkRateLimit
from app.services.rate_limiting_service import redis_client,redis_binary
from app.services.qrcode import QRCODE
import io
from app.services.ai_service import generate_slugs
from app.services.scraper_service import get_page_title
from arq import create_pool
from arq.connections import RedisSettings
from app.lifespan import lifespan


# set up FASTAPI instance
app = FastAPI(title='URL SHORTENER',lifespan=lifespan)

# start schedular
schedular = startSchedular()

# shutdown
atexit.register(lambda: shutdownSchedular(schedular))

# Create tables
Base.metadata.create_all(bind=engine)



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
    print('i am hitting your login for authentication....')
    user = db.query(User).filter(
        (user_data.username == User.username)
    ).first()

    if not user or not checkPassword(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # create token
    accessToken = createAccessToken(data={'sub':user.username})
   # return access token and its type
    return {'access_token': accessToken, 'token_type': 'bearer'}


#             SHORTENER             #
@app.post('/url')
async def create_short_url(request: Request, long_url: str = Form(...), valid_days : int = Form(30) , db: Session = Depends(get_db), current_user = Depends(getCurrentUser)):
    """
    check rate limit
    if true allow or block request
    """
    if not current_user:
        raise HTTPException(status_code=401, detail='No user found, Login first!')
    
    user_id = db.query(User.id).filter(User.username == current_user).first()
    # rate limit layer......
    checkRateLimit(request,user_id=user_id[0], max_req=5, time_window=60)

    """
    Here, We will generate random temperory code to return this to user immedietly,
    check if already available in db... if available re make the code
    """
    short_code = GenerateTemperoryCode()
    
    # this is worst condtion while loop is bomb for db -> replace come up with a optimized solution...
    # Check if code already exists
    while db.query(Url).filter(Url.shortUrl == short_code).first():  # ← shortUrl
        short_code = GenerateTemperoryCode()

    
    # expires at this..
    valid_days = datetime.utcnow() + timedelta(days=valid_days)
    
    # Save to database
    db_url = Url(
        tmp_code=short_code,    # ← shortUrl
        longUrl=long_url,
        expires_at = valid_days,
        user_id=user_id[0]
    )
    db.add(db_url)   # // insertion in db
    db.commit()   # //
    db.refresh(db_url)

    # now here we call the Queue [Worker]
    # hey, worker here is the short random code 
    # turn it into a ai slug when you have time
    try:
        print('Short code generated, Calling Redis [Queue Worker].... ')
        # connect to redis via request obj
        redis = request.app.state.redis
        await redis.enqueue_job('upgradeLinkTask',tmp_code=short_code,long_url=long_url)
        await redis.close()
    except Exception as e:
        print(f"Redis failed: {e}. User still gets working random link.")


    # return < 50ms    
    return {
        'shortUrl': f'http://localhost:8000/{short_code}',
        'temperory_code': short_code,
        'longUrl': long_url

    }



@app.get('/analytics')
def analytics(request: Request,db: Session = Depends(get_db),current_user = Depends(getCurrentUser)):
    user_id = db.query(User.id).filter(User.username == current_user).first()
    if not user_id:
        raise HTTPException(status_code=404, detail='user_id not found!')
    # rate limit layer
    checkRateLimit(request,user_id=user_id, max_req=5, time_window=60)
    
    data = db.query(Url.longUrl,Url.shortUrl,Url.clicks).filter(Url.user_id == user_id[0]).all()
    if not data:
        raise HTTPException(status_code=404,detail='No data found!')
    
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

# fire click tracking function
async def fireClickTracking(request, short_code):
    try:
        redis = request.app.state.redis
        await redis.enqueue_job('trackClickTask',short_code=short_code)
    except Exception as e:
        print(f'Erro calling Queue for tracking Clicks. ->: {e}')
        print('Redis Failed!')

@app.get('/{short_code}')
async def redirect_to_url(request:Request,short_code: str, db: Session = Depends(get_db)):
    """  apply reddis layer before db:
    if find in reddis redirct to long url:
    if not just go then to db find -> save to reddis now. 
    """
    print('Hitting redis....')
    # reddis layer 1
    row_id = redis_client.get(f'lookup:{short_code}') # short_code : row_id
    # redis layer 2 
    if row_id:
        url = redis_client.get(f'url:{row_id}') # -> row_id : longUrl
        if url:
            await fireClickTracking(request,short_code) # call queue to increment
            print('redirecting from redis')
            return RedirectResponse(url) 
    
    print('No Match find in Redis. -> Hitting db....')

    url_entry = db.query(Url).filter((Url.tmp_code == short_code) | (Url.shortUrl == short_code)).first()  # ← shortUrl
    if not url_entry:
        raise HTTPException(status_code=404, detail='URL not found')
    
    # check expiry
    if url_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410, detail='Link has been expired!')
    
    # Write to cache with remaining TTL
    time_remaining = (url_entry.expires_at - datetime.utcnow()).total_seconds()
    # redis layer 1 save short code with id
    row_id = redis_client.setex(f'lookup:{short_code}',int(time_remaining),url_entry.id)
    # redis layer 2 save id with URL
    key_val = redis_client.setex(f'url:{url_entry.id}',int(time_remaining),url_entry.longUrl)
    
    # call Worker Queue to trackclicks (fire and forget)
    fireClickTracking(request,short_code)
    # redirect to the 
    return RedirectResponse(url_entry.longUrl)

# qr code generator 
@app.get('/qrcode/{short_code}')
def qr_code(short_code : str, db : Session = Depends(get_db)):

    """ Args* :
            short_code: takes short_code as a parameter
        Returns* :
            generates qrcode for it..
    """

    url = db.query(Url).filter(Url.shortUrl == short_code).first()

    if not url:
        raise HTTPException(status_code=404,detail='url not found')
    if url.expires_at < datetime.utcnow():
        raise HTTPException(status_code=410,detail='url has expired!')
    
    # create instance
    qrcode = QRCODE()

    img_bytes = redis_binary.get(f'short_code:{short_code}')

    if img_bytes:
        return Response(
        content=img_bytes,
        media_type="image/png",
        headers={"Content-Type": "image/png"}
    )
    
    
    # generate qrcode
    qr_code_img = qrcode.generateQRcode(url.longUrl)

    # create instance of buff i.e memory in RAM
    buf = io.BytesIO()

    # write into buff
    qr_code_img.save(buf, format="PNG")

    # find the remainng time of link expiration?
    time_remaining = (url.expires_at - datetime.now()).total_seconds()
    # if not save to reddis
    redis_binary.setex(f'short_code:{short_code}',int(time_remaining),buf.getvalue())
    # reset buffer cursor to the  0 otherwise the read pointer is at the end
    buf.seek(0)

    return StreamingResponse(buf, media_type='image/png')

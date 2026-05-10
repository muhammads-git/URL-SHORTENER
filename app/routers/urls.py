from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse,Response
from sqlalchemy.orm import Session 
from app.database import get_db
from app.models import Url,User
from app.services.rate_limiting_service import checkRateLimit
from app.services.rate_limiting_service import redis_client,redis_binary
from app.services.qrcode import QRCODE
import io
from app.utils import GenerateTemperoryCode
from app.routers.auths import getCurrentUser
from datetime import datetime,timezone,timedelta

# create instance
router = APIRouter()

#             SHORTENER             #
@router.post('/url')
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

# fire click tracking function
async def fireClickTracking(request, short_code):
    try:
        redis = request.app.state.redis
        await redis.enqueue_job('trackClickTask',short_code=short_code)
    except Exception as e:
        print(f'Erro calling Queue for tracking Clicks. ->: {e}')
        print('Redis Failed!')


@router.get('/{short_code}')
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
    await fireClickTracking(request,short_code)
    # redirect to the 
    return RedirectResponse(url_entry.longUrl)

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


# create router
router = APIRouter()


@router.get('/analytics')
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



# qr code generator 
@router.get('/qrcode/{short_code}')
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

from fastapi import FastAPI,Depends,HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from app.utils import GenerateShortCode
from app.database import engine, Base, get_db
from app.models import Url
from sqlalchemy.orm import Session

app = FastAPI(title='URL SHORTENER')


# create table 
Base.metadata.create_all(bind=engine)

@app.get('/')
def hello():
   return {'message':"Helllo"}


@app.post('/url_shoterner')
def UrlShortener(long_url: str, db: Session = Depends(get_db)):
   # call function to generate short code
   shortCode = GenerateShortCode()
   while db.query(Url).filter(Url.shortCode == shortCode).first():
      short_code = GenerateShortCode()
   # save to database
   db_url = Url(shortCode=short_code, longUrl=long_url)
   db.add(db_url)
   db.commit()
   db.refresh(db_url)

   return {'shortUrl':f'http://localhost:8000/{shortCode}', 'code':short_code, 'longUrl':long_url }


@app.get('/{short_code}')
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(Url).filter(Url.shortCode == short_code).first()
    if not url_entry:
        raise HTTPException(statusCode=404, detail='URL not found')
    
    # Optional: increment click count
    # url_entry.clicks += 1
    # db.commit()
    
    return RedirectResponse(url_entry.long_url)





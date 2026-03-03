from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from app.utils import GenerateShortCode
from app.database import engine, Base, get_db
from app.models import Url
from sqlalchemy.orm import Session

app = FastAPI(title='URL SHORTENER')

# Create tables
Base.metadata.create_all(bind=engine)

@app.get('/')
def hello():
    return {"message": "Hello"}

@app.post('/url_shortener')
def create_short_url(long_url: str, db: Session = Depends(get_db)):
    short_code = GenerateShortCode()
    
    # Check if code already exists
    while db.query(Url).filter(Url.shortUrl == short_code).first():  # ← shortUrl
        short_code = GenerateShortCode()
    
    # Save to database
    db_url = Url(
        shortUrl=short_code,    # ← shortUrl
        longUrl=long_url
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    
    return {
        'shortUrl': f'http://localhost:8000/{short_code}',
        'code': short_code,
        'longUrl': long_url
    }

@app.get('/{short_code}')
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(Url).filter(Url.shortUrl == short_code).first()  # ← shortUrl
    
    if not url_entry:
        raise HTTPException(status_code=404, detail='URL not found')
    
    return RedirectResponse(url_entry.longUrl)
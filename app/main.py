from fastapi import FastAPI,requests,responses,HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
# 
from app.database import url_db
from app.utils import GenerateShortCode

app = FastAPI(title='URL SHORTENER')


@app.get('/')
def hello():
   return {'message':"Helllo"}


@app.post('/url_shoterner')
def UrlShortener(long_url: str):
   # call function to generate short code
   shortCode = GenerateShortCode
   # save into dict as kye : value pairs
   url_db[shortCode] = long_url
   return {'shortUrl':f'http//localhost:8000{shortCode}', 'code':{shortCode} }


@app.get('/{ShortCode}')
def redirect_to_code(shortCode: str):
   if not shortCode in url_db:
      raise HTTPException(status_code=404, detail='URL not found')

   return RedirectResponse(url_db[shortCode])





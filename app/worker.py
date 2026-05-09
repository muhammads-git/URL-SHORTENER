import asyncio
from arq.connections import RedisSettings
from arq import create_pool
from fastapi import HTTPException
from app.models import Url,User
from app.database import SessionLocal
from app.services.ai_service import generate_slugs
from app.services.scraper_service import get_page_title
import string,random
from app.utils import isTempCode

# generates suffix
def GenerateShortSuffix(length=4):
   chars = string.ascii_letters + string.digits
   return ''.join(random.choices(chars, k=length))


async def upgradeLinkTask(ctx,tmp_code,long_url):
   """ this is queue job......."""
   try:
      title = await get_page_title(long_url) # scrap the title of site
      ai_slug = await generate_slugs(title)

   except Exception as e:
      print(f'{e}')
      print(f'[Worker] Error generating ai_slug, keep random code!')
      return

   """ now open a private db session"""
   db = SessionLocal()

   try:
      
      # check for collision
      existingCode = db.query(Url).filter(Url.shortUrl == ai_slug).first()

      if existingCode:
         # code exist either recall ai or keep the random
         print(f'Slug already taken...')
         # generate suffix
         suffix = GenerateShortSuffix()
         # concatenate with slug
         ai_slug =f'{ai_slug}-{suffix}'
         print(f'suffixed slug {ai_slug}')
      
      temperoryCode = db.query(Url).filter(Url.tmp_code == tmp_code).first()
      if temperoryCode:
         print(f"[Worker] 🔄 Creating slug for -> {tmp_code} = {ai_slug}")
            # update the code to short slug ai generated
         temperoryCode.shortUrl = ai_slug
         db.commit()
      else:
            print("[Worker] Could not find original link! Weird.")
   finally:
      db.close()



async def trackClickTask(ctx,short_code):
   """ let the queue do this.."""
   # private db session
   db = SessionLocal()
   
   try:
      # check if code is temp or slug
      if isTempCode(short_code):
         print('checking is tempcode..')
         url = db.query(Url).filter(Url.tmp_code == short_code).first()
      else:
         url = db.query(Url).filter(Url.shortUrl == short_code).first()

      if url:

         print(f"[Worker] 🔄 Tracking -> {short_code} +1 is incremented.")
         # update the click
         url.clicks += 1
         db.commit()
      else:
         print("[Worker] Could not find original link to track clicks! Weird.")
   finally:
      db.close()


class WorkerSettings:
   redis_settings = RedisSettings(host='127.0.0.1',port=6379)
   functions = [upgradeLinkTask,trackClickTask]
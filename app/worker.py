import asyncio
from arq.connections import RedisSettings
from arq import create_pool
from fastapi import HTTPException
from app.models import Url,User
from app.database import SessionLocal
from app.services.ai_service import generate_slugs
from app.services.scraper_service import get_page_title


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
      
      else:
         temperoryCode = db.query(Url).filter(Url.shortUrl == tmp_code).first()
         if temperoryCode:
            print(f"[Worker] 🔄 Upgrading {tmp_code} -> {ai_slug}")
            # update the code to short slug ai generated
            temperoryCode.shortUrl = ai_slug
            db.commit()
         else:
                print("[Worker] Could not find original link! Weird.")
   finally:
      db.close()


# track clicks

async def trackClickTask(ctx,short_code):
   """ let the queue do this.."""
   # private db session
   db = SessionLocal()

   try:
      url = db.query(Url).filter(Url.shortUrl == short_code).first()
      if url:
         print(f"[Worker] 🔄 Tracking -> {short_code}")
         # update the click
         url.clicks += 1
      else:
         print("[Worker] Could not find original link to track clicks! Weird.")
         raise HTTPException(status_code=404)
   finally:
      db.close()


class WorkerSettings:
   redis_settings = RedisSettings(host='127.0.0.1',port=6379)
   functions = [upgradeLinkTask]
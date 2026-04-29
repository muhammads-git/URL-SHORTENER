import asyncio
from arq.connections import RedisSettings
from arq import create_pool

from app.models import Url,User
from app.database import SessionLocal
from app.services.ai_service import generate_slugs
from app.services.scraper_service import get_page_title


async def upgradeLinkTask(ctx,tmp_code,long_url):
   """ this is queue job......."""
   pass

def hello():
   return 'hell'


from contextlib import asynccontextmanager
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI
from redis.backoff import ExponentialBackoff
from redis.retry import Retry

# this has to be called as startup and shutdown by python
@asynccontextmanager
async def lifespan(app : FastAPI): 

   print("🚨 LIFESPAN STARTUP: CONNECTING TO REDIS...")

   app.state.redis = await create_pool(RedisSettings(host='127.0.0.1',port=6379))
   
   yield   # PAUSE the above code runs till the app is alive

   await app.state.redis.close()

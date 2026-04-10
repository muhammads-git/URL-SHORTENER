from redis import Redis
from fastapi import HTTPException, Request 
from sqlalchemy.orm import Session
from app.models import User
# from app.main import getCurrentUser

redis_client = Redis(
   host='localhost',
   port=6379,
   decode_responses=True
)


def getClientIdentifier(request : Request) -> str:
   """
   get a unique identifier for client
   if logged in use USER ID
   or
   if not user IP 
   """
   # get user id
   # username = getCurrentUser()
   # if not username:
   #    raise HTTPException(detail='User not found, we will user IP for rate limiting...')
   
   # user_id = db.query(User).filter(User.username == username).first()
   # if not user_id:
   #    raise HTTPException(detail='User id not found.')
   
   

   client_ip = request.client.host
   # print(f'CLIENT IP ADDRESS: {client_ip}')
   return f'rate_limit: {client_ip}'


def checkRateLimit(request: Request, max_req: int = 5, time_window: int =60) -> bool:
   """
   this function checks rate limit

   Args*
      takes request obj
      max request 
      time window
   
   returns*
      allowed or block by 429 status code if limit exceeds
   """


   # get client id
   key = getClientIdentifier(request)

   # get current count
   current_count = redis_client.get(key)

   if not current_count:
      # set current count to 1 with expiration time
      redis_client.setex(key, time_window, 1)
      return True
   

   # convert to int in-case
   current_count = int(current_count)

   # check limit
   if current_count >= max_req:
      # get ttl 
      ttl = redis_client.ttl(key)
      # raise http exception with 429 status
      raise HTTPException(
         status_code=429,
         detail=f'Rate limit exceeded, please try again in {ttl} seconds.'
      )
   
   # or increament in counter
   redis_client.incr(key)
   return True






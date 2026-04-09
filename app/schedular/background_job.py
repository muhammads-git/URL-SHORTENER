from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from app.services.cleanup_service import cleanUpExpiredLinks
from app.database import SessionLocal

""" cleanup jobs"""
def cleanUpJob():
   
   """ call the cleanUp function to remove the links"""
   db = SessionLocal()
   try:
      deleted_urls = cleanUpExpiredLinks(db)
      if deleted_urls:
         print(f'Jobs delted: {deleted_urls}')
   except Exception as e:
      print(f'Error cleaning Up jobs: {e}')
   finally:
      db.close()



""" start schedular """

def startSchedular():
   schedular = BackgroundScheduler()
   schedular.add_job(id='clean_up',func=cleanUpJob,trigger='interval', hours=24)
   # start
   schedular.start()

   print('Schedular started will cleanup, expired Links!')
   return schedular


def shutdownSchedular(schedular):
   if schedular:
      schedular.shutdown()
      print("schedular stopped!")



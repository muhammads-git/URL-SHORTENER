import string, random
from app.database import get_db
from app.models import Url, User

"""
GENERATE THE SHORT CODE...
"""

def GenerateShortCode(length=6):
   chars = string.ascii_letters + string.digits
   return ''.join(random.choices(chars, k=length))


"""
FUNCTION FOR DELETING EXPIRED LINKS
"""

# def removeExpiredLinks(expire_url_id):
#    db = get_db()

#    try:

#       url = db.query(Url).filter(Url.id == expire_url_id).first()
#       db.delete(url)
#       db.commit()
#       print('URL has been deleted from db!')

#    except Exception as e:
#       return {
#          'error':str(e)
#       }
      



   

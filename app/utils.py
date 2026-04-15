import string, random
from app.database import get_db
from app.models import Url, User

"""
GENERATE THE SHORT CODE
using string,random with a lenght of 6 bytes...
"""

def GenerateShortCode(length=6):
   chars = string.ascii_letters + string.digits
   return ''.join(random.choices(chars, k=length))




   

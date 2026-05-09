import string, random
from app.database import get_db
from app.models import Url, User

"""
GENERATE THE SHORT CODE
using string,random with a lenght of 6 bytes...
"""

# def GenerateShortSuffix(length=4):
#    chars = string.ascii_letters + string.digits
#    return ''.join(random.choices(chars, k=length))

def GenerateTemperoryCode(lenght=5):
   tmp ='tmp'
   chars = tmp + string.digits
   code = ''.join(random.choices(chars,k=lenght))
   return code

# check if the code is slug or tempCode
def isTempCode(short_code:str) -> bool:
   # check if - present then return False
   for char in short_code:
      if char == '-':
         return False
   return True


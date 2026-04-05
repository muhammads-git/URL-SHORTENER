import string, random


"""
GENERATE THE SHORT CODE...
"""

def GenerateShortCode(length=6):
   chars = string.ascii_letters + string.digits
   return ''.join(random.choices(chars, k=length))



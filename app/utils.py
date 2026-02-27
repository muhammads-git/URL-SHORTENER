import string, random


# url shortenere

def GenerateShortCode(length=6):
   chars = string.ascii_letters + string.digits
   return ''.join(chars, k=length)



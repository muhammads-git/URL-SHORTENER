from passlib.context import CryptContext
import bcrypt
from jose import JWTError,jwt
from dotenv import load_dotenv
import os
load_dotenv()

### GET .env data
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# pwd_context = CryptContext(schemes=['bcrypt_sha256'], deprecated='auto')

# def hashPassword(password: str) -> str:
#    return pwd_context.hash(password)

# def  verifyPassword(plain: str, hashed: str) -> bool:
#    return pwd_context.verify(plain, hashed)

######################### HASHING ###########################33
def hashPassword(password: str) -> str:
   salt = bcrypt.gensalt()
   hashed = bcrypt.hashpw(password.encode('utf-8'),salt)
   return hashed.decode('utf-8')  # store as string

def checkPassword(plainPassword: str, hashedPassword: str) -> bool:
   return bcrypt.checkpw(plainPassword.encode('utf-8'),hashedPassword.encode('utf-8'))
from passlib.context import CryptContext
import bcrypt
from jose import JWTError,jwt
from dotenv import load_dotenv
import os
from datetime import datetime , timedelta
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
   # create saltvi
   salt = bcrypt.gensalt()
   hashed = bcrypt.hashpw(password.encode('utf-8'),salt)
   return hashed.decode('utf-8')  # store as string

def checkPassword(plainPassword: str, hashedPassword: str) -> bool:
   return bcrypt.checkpw(plainPassword.encode('utf-8'),hashedPassword.encode('utf-8'))



#____________________JWT TOKEN FUNCTION ____________________#
def createAccessToken(data: dict, expires_delta: timedelta = None):
    """
    Create a JWT token with expiration.
    
    Args:
        data: Dictionary containing user info (usually {"sub": username})
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
     
     
    toEncode = data.copy()

    # Set expiry time

   #  if expires_delta:
   #     expire = datetime.utcnow() + expires_delta
   #  else:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # add to existing dict
    toEncode.update({'exp':expire})

    # create token
    encodedJWT = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)
    print("Encoded tokens: ", encodedJWT) 
    return encodedJWT

def decodeToken(token: str):
   
    """
    Decode and verify JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Username if token is valid, None otherwise
    """

    try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
       username: str = payload.get('sub')
       return username
    except JWTError:
       return None
    

def getTokenExpiration():
   """ helper to get DEFAULT expiration time """
   return datetime.utcnow + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

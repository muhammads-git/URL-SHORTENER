from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from app.utils import GenerateShortCode
from app.database import engine, Base, get_db
from app.models import Url, User
from sqlalchemy.orm import Session
from app.auths.auths import hashPassword, checkPassword,ACCESS_TOKEN_EXPIRE_MINUTES,createAccessToken,getTokenExpiration,decodeToken
from app.schemas.schemas import UserCreate

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

app = FastAPI(title='URL SHORTENER')


# Create tables
Base.metadata.create_all(bind=engine)

@app.get('/')
def hello():
    return {"message": "Hello"}


# ________________________REGISTRATIONS ROUTES___________________________#
@app.post('/register')
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # // check if user exists already...
    existing = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()

    # check 
    if existing:
        # check username or email taken
        if existing.username == user_data.username:
            detail = 'Username already taken!'
        else:
            detail = 'Email already taken!'
        raise HTTPException(status_code=404, detail=detail)
    
    print(f"Checking registration for: {user_data.username}, {user_data.email}")
    if existing:
        print(f"FOUND MATCH: username={existing.username}, email={existing.email}")
    else:
        print("No match found - this username/email is available")

    # hash password................
    hashedPassword = hashPassword(user_data.password)

    # create user
    newUser = User(
        username = user_data.username,
        email = user_data.email,
        password = hashedPassword
    )
    # save to db
    db.add(newUser)
    db.commit()
    db.refresh(newUser)

    return {'success': True, 'message':'User created!'}

# Login route
@app.post('/login')
def login(user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # now the OAuth2PasswordRequestForm will automatically handle forms
    user = db.query(User).filter(
        (user_data.username == User.username)
    ).first()

    if not user or not checkPassword(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # create token

    accessToken = createAccessToken(data={'sub':user.password})


   # return access token and its type
    return {'access_token': accessToken, 'token_type': 'bearer'}

# Protected route
@app.get('/users/me')
def read_users_me(token: str = Depends(oauth2_scheme)):
    username = decodeToken(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"username": username}


#             SHORTENER             #
@app.post('/url_shortener')
def create_short_url(long_url: str, db: Session = Depends(get_db)):
    short_code = GenerateShortCode()
    
    # Check if code already exists
    while db.query(Url).filter(Url.shortUrl == short_code).first():  # ← shortUrl
        short_code = GenerateShortCode()
    
    # Save to database
    db_url = Url(
        shortUrl=short_code,    # ← shortUrl
        longUrl=long_url
    )
    db.add(db_url)   # // insertion in db
    db.commit()   # //
    db.refresh(db_url)
    
    return {
        'shortUrl': f'http://localhost:8000/{short_code}',
        'code': short_code,
        'longUrl': long_url
    }

@app.get('/{short_code}')
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(Url).filter(Url.shortUrl == short_code).first()  # ← shortUrl
    
    if not url_entry:
        raise HTTPException(status_code=404, detail='URL not found')
    
    url_entry.clicks += 1
    db.commit() # commit

    return RedirectResponse(url_entry.longUrl)


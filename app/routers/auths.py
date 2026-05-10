from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, FileResponse, StreamingResponse,Response
from sqlalchemy.orm import Session 
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from app.auths.auth import hashPassword,checkPassword,ACCESS_TOKEN_EXPIRE_MINUTES,createAccessToken,getTokenExpiration,decodeToken
from app.database import get_db
from app.models import Url,User
from app.schemas.schema import UserCreate

# instance router
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')
# get current user
def getCurrentUser(token: str = Depends(oauth2_scheme)):
    username = decodeToken(token)
    if not username:
        raise HTTPException(
            status_code=404,
            detail='Invalid Token or no such user found'
        )
    else:
        return username

# ROUTESSSSSSSSSSSSS
@router.post('/register')
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
@router.post('/login')
def login(user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # now the OAuth2PasswordRequestForm will automatically handle forms
    print('i am hitting your login for authentication....')
    user = db.query(User).filter(
        (user_data.username == User.username)
    ).first()

    if not user or not checkPassword(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # create token
    accessToken = createAccessToken(data={'sub':user.username})
   # return access token and its type
    return {'access_token': accessToken, 'token_type': 'bearer'}

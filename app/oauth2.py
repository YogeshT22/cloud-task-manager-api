# --------------------------------------
# purpose: OAuth2 utility functions for token creation and verification
# target: Cloud Task Manager API
# personal project for learning backend development with FastAPI and PostgreSQL.
# referring docs, making comments for better understanding later.
# --------------------------------------

# app/oauth2.py
# importing jwt, datetime, timedelta, timezone...
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .config import settings


# OAuth2PasswordBearer is a class we can use to handle the OAuth2 "password flow"
# DOCS_MENTIONED: can create bugs if tokenUrl is not correct!
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

# Load settings from config.py by creating variables and calling settings attributes.
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# function to create access token.
# pattern is create function -> copy data -> set expiration -> encode JWT -> return token
# DEVNOTE: data parameter is a dictionary containing the payload for the token.
# stupid code formatter making it difficult to read the code!!


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# function to verify access token.
# pattern is verify function -> decode JWT -> extract user info -> handle exceptions -> return token data
# DEVNOTE: credentials_exception is raised if token is invalid or expired.
# Took help from official docs for this function implementation.


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = {"id": user_id}  # Can be a more complex schema if needed
    except JWTError:
        raise credentials_exception
    return token_data

# Dependency function to get the current user based on the token.


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail=f"Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    token_data = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(
        models.User.id == token_data["id"]).first()

    return user

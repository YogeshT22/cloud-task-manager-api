# --------------------------------
# purpose: utility functions for password hashing and verification using argon2.
# target: Cloud Task Manager API
# personal project for learning backend development with FastAPI and PostgreSQL.
# --------------------------------

# app/utils.py

# simply import CryptContext from passlib.context
from passlib.context import CryptContext

# Tell passlib to use 'argon2' as the default scheme. This bypasses bcrypt completely.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# function to hash a password
# pattern is hash function -> use pwd_context to hash -> return hashed password


def hash(password: str):
    return pwd_context.hash(password)

# to verify a plain password against a hashed password
# pattern is verify function -> use pwd_context to verify -> return boolean
# referred docs to know about pwd_context.verify function, it's usage.


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

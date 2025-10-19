# app/utils.py

from passlib.context import CryptContext

# Tell passlib to use 'argon2' as the default scheme. This bypasses bcrypt completely.
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

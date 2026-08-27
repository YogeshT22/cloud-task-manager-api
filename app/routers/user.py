# app/routers/user.py

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError  # Import this

from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])

# Create a new user endpoint. "/tasks/" is the endpoint for creating a new user. The status code is set to 201 (Created) and the response model is set to UserResponse.


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse
)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hash the password before storing it in the database
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    # Create a new user instance using the User model and the data from the request
    new_user = models.User(**user.dict())

    db.add(new_user)

    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:  # Catch the specific database error
        db.rollback()  # Rollback the failed transaction
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email: {user.email} already exists",
        )

    return new_user

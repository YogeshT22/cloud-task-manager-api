# app/schemas.py

from pydantic import BaseModel
from datetime import datetime

# This is a base model. We use it to share common attributes
# between other schemas to avoid repetition (DRY principle).


class TaskBase(BaseModel):
    title: str
    content: str
    completed: bool = False  # Provide a default value

# This schema is used when a user sends data to create a task.
# It inherits all fields from TaskBase.


class TaskCreate(TaskBase):
    pass

# This schema is used when we return a task in an API response.
# It includes the database-generated fields like 'id' and 'created_at'.


class TaskResponse(TaskBase):
    id: int
    created_at: datetime

    # This 'Config' class tells Pydantic to work with SQLAlchemy models.
    # It enables Pydantic to read data even if it's not a dict, but an ORM object.
    class Config:
        from_attributes = True  # Formerly orm_mode = True

# USER SCHEMAS


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

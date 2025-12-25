# ---------------------------------
# purpose: Define database models for the Cloud Task Manager API
# target: Cloud Task Manager API
# personal project for learning backend development with FastAPI and PostgreSQL.
# referring docs, making comments for better understanding later.
# --------------------------------


# app/models.py

# DevNote: Add 'ForeignKey' and 'relationship' to the imports
from sqlalchemy import Column, Integer, String, Boolean, text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from .database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    completed = Column(Boolean, server_default='FALSE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))

    # --- THIS IS THE MISSING PIECE ---
    # This column links a task to a user.
    owner_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), nullable=False)

    # DOCS_MENTIONED: This creates a property on the Task model to easily access the related User object.
    owner = relationship("User")
    # ---------------------------------

# Define the User model!


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
# DEVNOTE__: we create a class for each table in the database.
# DEVNOTE__:var = Column(DataType, options) is pattern to define columns in SQLAlchemy models.
# DEVNOTE__:we have different parameters that can be found in docs easily..!

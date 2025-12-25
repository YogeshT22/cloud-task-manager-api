# filepath: app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


# This is the connection URL for SQLAlchemy afaik!!
# "Format" should be: 'postgresql://<user>:<password>@<hostname>:<port>/<dbname>'

DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

# The 'engine' is the core interface to the database.
engine = create_engine(DATABASE_URL)

# session is a temporary connection to the database for performing transactions!
# a configurable session class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All of models (like the Task class) will inherit from this Base class.
Base = declarative_base()


# Dependency function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

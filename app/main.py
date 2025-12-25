# ---------------------------------
# purpose: main application file for FastAPI app
# target: Cloud Task Manager API
# personal project for learning backend development with FastAPI and PostgreSQL.
# --------------------------------

# app/main.py

# 1. Import the FastAPI class from the fastapi library
from fastapi import FastAPI
# here i should Import models to ensure they are registered before creating tables(mentioned in official docs! lol)
from . import models
from .database import engine  # Imports the engine from database.py
from .routers import task, user, auth


# DOCS_MENTIONED: "SQLAlchemy will look at all the classes that inherit from Base (in models.py)
# and generate the corresponding SQL "CREATE TABLE" statements."
models.Base.metadata.create_all(bind=engine)


# 2. Create an instance of the FastAPI class
# DOCS_MENTIONED:This 'app' instance will be the main point of interaction for creating our API.

# DOUBT__: instance here is like server? answer: Yes, the 'app' instance created from the FastAPI class acts as the
# -- main application or server that will handle incoming HTTP requests and route them to the appropriate functions.
app = FastAPI(
    title="Cloud Task Manager API",
    description="A simple API to manage tasks and users.",
    version="0.1.0"
)

app.include_router(auth.router)  # we add auth router
app.include_router(user.router)  # we add user router
app.include_router(task.router)  # we add task router after auth and user.

# Include the router in our main app instance.
# All endpoints defined in 'task.router' will now be part of our application.
app.include_router(task.router)


# 3. Define a "path operation decorator"
# @app.get("/") tells FastAPI that the function below is in charge of
# handling requests that go to the path "/" using a GET method.

# DOUBT__: / is the root path of the API.


@app.get("/")
def read_root():
    """
    This is the root endpoint of the API.
    It returns a welcome message.
    """
# 4. Return the content
# FastAPI will automatically convert this Python dictionary into a JSON response.
# key value pair in dictionary used in return to create JSON response, always we use return to send response back to client, in backend development.
    return {"message": "Welcome to the Cloud Task Manager API!"}

# DEVNOTE: You can add another simple endpoint for practice later


# This is simple health check endpoint function.
@app.get("/health")
def health_check():
    """
    A simple health check endpoint to confirm the API is running.
    """
    return {"status": "ok"}

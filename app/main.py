# ---------------------------------
# purpose: main application file for FastAPI app
# target: Distributed Task Processing API
# personal project for learning backend development with FastAPI and PostgreSQL.
# --------------------------------

# app/main.py

# 1. Import the FastAPI class from the fastapi library
# pyrefly: ignore [missing-import]
from fastapi import FastAPI
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# here i should Import models to ensure they are registered before creating tables(mentioned in official docs! lol)
from . import models
from .database import engine  # Imports the engine from database.py
from .routers import task, user, auth
from . import celery_app, tasks  # Import Celery for task autodiscovery


# DOCS_MENTIONED: "SQLAlchemy will look at all the classes that inherit from Base (in models.py)
# and generate the corresponding SQL "CREATE TABLE" statements."
models.Base.metadata.create_all(bind=engine)

# 2. Create an instance of the FastAPI class
# DOCS_MENTIONED:This 'app' instance will be the main point of interaction for creating our API.

# -- main application or server that will handle incoming HTTP requests and route them to the appropriate functions.
app = FastAPI(
    title="Distributed Task Processing Platform",
    description="A containerized platform for task management and distributed background processing.",
    version="0.1.0"
)

# CORS: Allow the Next.js frontend (localhost:3000) to call this API from a browser.
# Browsers enforce the Same-Origin Policy — without this header, every fetch() call
# from the frontend is blocked, even though curl/Postman work fine.
# allow_credentials=True is required because we send Authorization: Bearer headers.

# what is middleware: Middleware is a function that runs before or after each request. It can modify the request or response, or perform other actions like logging or authentication. In this case, we are using CORS middleware to handle cross-origin requests.

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Note__: In production we should restrict the origins to only the domains that need access to the API.

# in below what we doing? answer: we are including the routers for auth, user, and task into our main FastAPI application instance. This allows us to organize our endpoints into separate modules and keep our codebase clean and maintainable.
app.include_router(auth.router)  # we add auth router
app.include_router(user.router)  # we add user router
app.include_router(task.router)  # we add task router after auth and user.

# Include the router in our main app instance.
# All endpoints defined in 'task.router' will now be part of our application.
app.include_router(task.router)

# 3. Define a "path operation decorator"
# @app.get("/") tells FastAPI that the function below is in charge of handling requests that go to the path "/" using a GET method.

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
    return {"message": "Welcome to the Distributed Task Processing Platform!"}

# DEVNOTE: You can add another simple endpoint for practice later


# This is simple health check endpoint function.
@app.get("/health")
def health_check():
    """
    A simple health check endpoint to confirm the API is running.
    """
    return {"status": "ok"}

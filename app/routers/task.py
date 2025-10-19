# app/routers/task.py

from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(
    prefix="/tasks",
    tags=['Tasks']
)

# CREATE A TASK

# what is post request? answer: A POST request is an HTTP method used to send data to a server to create a new resource. In RESTful APIs, POST requests are commonly used to create new entries in a database, such as adding a new task, user, or item. The data sent in the body of the POST request typically contains the information needed to create the resource.


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TaskResponse, operation_id="create_task")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    # Create a new SQLAlchemy model instance from the Pydantic schema
    new_task = models.Task(**task.dict())
    db.add(new_task)  # Add the new task to the session
    db.commit()      # Commit the transaction to the database
    # Refresh the instance to get the new ID and created_at
    db.refresh(new_task)
    return new_task

# GET ALL TASKS


@router.get("/", response_model=List[schemas.TaskResponse], operation_id="get_all_tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
    return tasks

# GET A SPECIFIC TASK


@router.get("/{id}", response_model=schemas.TaskResponse, operation_id="get_one_task")
def get_task(id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id: {id} was not found")
    return task

# DELETE A TASK


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="delete_task")
def delete_task(id: int, db: Session = Depends(get_db)):
    task_query = db.query(models.Task).filter(models.Task.id == id)
    task = task_query.first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id: {id} does not exist")
    task_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# UPDATE A TASK


@router.put("/{id}", response_model=schemas.TaskResponse, operation_id="update_task")
def update_task(id: int, updated_task: schemas.TaskCreate, db: Session = Depends(get_db)):
    task_query = db.query(models.Task).filter(models.Task.id == id)
    task = task_query.first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id: {id} does not exist")
    task_query.update(updated_task.dict(), synchronize_session=False)
    db.commit()
    return task_query.first()

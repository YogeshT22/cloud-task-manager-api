# app/routers/task.py

from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/tasks",
    tags=['Tasks']
)

# CREATE A TASK
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TaskResponse, operation_id="create_task")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    # The 'current_user' is now available thanks to our dependency
    # We pass the owner_id when creating the new task
    new_task = models.Task(owner_id=current_user.id, **task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# GET ALL TASKS
@router.get("/", response_model=List[schemas.TaskResponse], operation_id="get_all_tasks")
def get_tasks(db: Session = Depends(get_db),
              current_user: models.User = Depends(oauth2.get_current_user)):
    # Only fetch tasks owned by the currently logged-in user
    tasks = db.query(models.Task).filter(models.Task.owner_id == current_user.id).all()
    return tasks

# GET A SPECIFIC TASK
@router.get("/{id}", response_model=schemas.TaskResponse, operation_id="get_one_task")
def get_task(id: int, db: Session = Depends(get_db),
             current_user: models.User = Depends(oauth2.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id: {id} was not found")

    # Check if the user owns this task
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    return task

# DELETE A TASK
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, operation_id="delete_task")
def delete_task(id: int, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    task_query = db.query(models.Task).filter(models.Task.id == id)
    task = task_query.first()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id: {id} does not exist")

    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    task_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# UPDATE A TASK
@router.put("/{id}", response_model=schemas.TaskResponse, operation_id="update_task")
def update_task(id: int, updated_task: schemas.TaskCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    task_query = db.query(models.Task).filter(models.Task.id == id)
    task = task_query.first()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id: {id} does not exist")

    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    task_query.update(updated_task.dict(), synchronize_session=False)
    db.commit()
    return task_query.first()
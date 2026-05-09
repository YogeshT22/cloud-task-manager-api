# app/routers/task.py

from fastapi import Depends, HTTPException, status, APIRouter, Response
from sqlalchemy.orm import Session
from typing import List
import logging

from .. import models, schemas, oauth2
from ..database import get_db
from ..tasks import send_task_reminder


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/tasks",
    tags=['Tasks']
)

# CREATE A TASK


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.TaskResponse, operation_id="create_task")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(oauth2.get_current_user)):
    new_task = models.Task(owner_id=current_user.id, **task.dict())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# GET ALL TASKS


@router.get("/", response_model=List[schemas.TaskResponse], operation_id="get_all_tasks")
def get_tasks(db: Session = Depends(get_db),
              current_user: models.User = Depends(oauth2.get_current_user)):
    tasks = db.query(models.Task).filter(
        models.Task.owner_id == current_user.id).all()
    return tasks

# GET A SPECIFIC TASK


@router.get("/{id}", response_model=schemas.TaskResponse, operation_id="get_one_task")
def get_task(id: int, db: Session = Depends(get_db),
             current_user: models.User = Depends(oauth2.get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id: {id} was not found")

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

# SEND TASK REMINDER (Background Job)


@router.post("/{id}/remind", status_code=status.HTTP_202_ACCEPTED, operation_id="send_task_reminder")
def send_reminder(id: int, db: Session = Depends(get_db),
                  current_user: models.User = Depends(oauth2.get_current_user)):
    """
    Trigger a background task to send a reminder for the specified task.
    
    Returns 202 Accepted immediately; the reminder is processed asynchronously.
    
    Example response:
    {
        "task_id": "abc123def456...",
        "status": "sent_to_queue",
        "detail": "Reminder queued for background processing"
    }
    """
    task = db.query(models.Task).filter(models.Task.id == id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id: {id} was not found")

    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    try:
        # Dispatch background task to Celery worker
        celery_task = send_task_reminder.delay(task_id=id, user_id=current_user.id)
        logger.info(f"Task reminder queued: {celery_task.id} for task {id}")
        
        return {
            "task_id": celery_task.id,
            "status": "sent_to_queue",
            "detail": f"Reminder for task '{task.title}' queued for background processing"
        }
    except Exception as e:
        logger.error(f"Error queueing reminder task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not queue task - background worker may be unavailable"
        )

# app/tasks.py
"""
Celery background tasks for the Cloud Task Manager API.

Demonstrates:
- Distributed task processing with retries
- Exponential backoff on failure
- Idempotent task execution
- Task logging and monitoring
"""

# i can rename this file to celery_tasks.py or background_tasks.py, but tasks.py is a common convention in Celery projects, so i'll keep it as tasks.py for now.
import logging
from celery import shared_task
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Task, User

# Configure logging for tasks
logger = logging.getLogger(__name__)

# Task Definitions
# shared tasks are used so that they can be discovered by Celery workers without needing to import the module directly.
# is this dev done it or from docs? answer: This is a common pattern in Celery documentation and best practices. Using `@shared_task` allows tasks to be registered with the Celery app without requiring direct imports, which is useful for modularity and avoiding circular dependencies.


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds first
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,  # Max retry delay: 10 minutes
    retry_jitter=True,  # Add randomness to prevent thundering herd
)
# send reminder task for incomplete tasks
def send_task_reminder(self, task_id: int, user_id: int):
    """
    Background task to send a reminder for an incomplete task.

    Features:
    - Retries up to 3 times with exponential backoff
    - Idempotent: safe to retry without side effects
    - Includes logging for observability

    Args:
        task_id: ID of the task to send reminder for
        user_id: ID of the user who owns the task

    Raises:
        Exception: Task failures trigger automatic retries
    """
    db = SessionLocal()

    try:
        # Fetch task and user from database
        task = db.query(Task).filter(Task.id == task_id).first()
        user = db.query(User).filter(User.id == user_id).first()

        if not task:
            logger.warning(f"Task {task_id} not found; skipping reminder")
            return {"status": "not_found", "task_id": task_id}

        if not user:
            logger.warning(f"User {user_id} not found; skipping reminder")
            return {"status": "user_not_found", "user_id": user_id}

        # Idempotency check: don't remind if task is already completed
        if task.completed:
            logger.info(
                f"Task {task_id} already completed; no reminder needed")
            return {"status": "already_completed", "task_id": task_id}

        # Simulate sending a reminder email (in production, use actual email service)
        logger.info(
            f"Sending reminder for task '{task.title}' to user {user.email} "
            f"(Task ID: {task_id}, Owner: {user_id})"
        )

        # In a real system, you'd call an email service here:
        # send_email(
        #     to=user.email,
        #     subject=f"Reminder: {task.title}",
        #     body=f"You have an incomplete task: {task.content}"
        # )

        return {
            "status": "success",
            "task_id": task_id,
            "user": user.email,
            "task": task.title,
            "sent_at": datetime.timezone.utc().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Error sending reminder for task {task_id}: {str(exc)}")

        # Retry with exponential backoff
        # max_retries=3 ensures we don't retry forever
        raise self.retry(exc=exc)

    finally:
        db.close()

# again shared_task is used here to allow Celery to discover this task without needing to import the module directly. This is a common pattern in Celery applications, especially when tasks are defined in separate modules or packages. It helps avoid circular imports and keeps the code modular.
# how the celery works, why concerned about importing directly? answer: Celery uses a worker process to execute tasks asynchronously. When you define a task using `@shared_task`, it registers the task with the Celery app without requiring the module to be imported directly. This is important because if you have multiple modules that import each other (circular imports), it can lead to import errors or unexpected behavior. By using `@shared_task`, you ensure that the task is discoverable by Celery workers without needing to worry about the order of imports, making the codebase more modular and maintainable.


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=30,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def mark_overdue_tasks(self):
    """
    Scheduled task to identify and log overdue tasks.

    In a production system, this could:
    - Send batch reminders
    - Escalate to team leads
    - Trigger SLA warnings
    - Archive old completed tasks

    Features:
    - Runs periodically via Celery Beat
    - Fault-tolerant with retries
    - Includes metrics for monitoring
    """
    db = SessionLocal()

    try:
        # Find incomplete tasks (in practice, you'd add a 'due_date' field to Task model)
        incomplete_tasks = db.query(Task).filter(Task.completed == False).all()

        logger.info(f"Found {len(incomplete_tasks)} incomplete tasks")

        # Example: log task details for monitoring
        for task in incomplete_tasks[:5]:  # Log first 5
            logger.debug(
                f"Incomplete task: {task.title} (ID: {task.id}, "
                f"Created: {task.created_at}, Owner: {task.owner_id})"
            )

        return {
            "status": "success",
            "incomplete_task_count": len(incomplete_tasks),
            "checked_at": datetime.timezone.utc().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Error in mark_overdue_tasks: {str(exc)}")
        raise self.retry(exc=exc)

    finally:
        db.close()


@shared_task(bind=True, max_retries=1)
def sync_task_metadata(self, task_id: int):
    """
    Example task for keeping task metadata in sync with external systems.

    Could be used for:
    - Syncing with Slack/Teams
    - Updating analytics dashboards
    - Pushing to webhooks
    - Exporting to data warehouse
    """
    db = SessionLocal()

    try:
        task = db.query(Task).filter(Task.id == task_id).first()

        if not task:
            logger.warning(f"Task {task_id} not found for sync")
            return {"status": "not_found"}

        logger.info(f"Syncing metadata for task {task_id}: {task.title}")

        # Example: could make HTTP call to external API
        # response = requests.post(
        #     "https://external-api.com/tasks",
        #     json={"id": task.id, "title": task.title, "completed": task.completed}
        # )

        return {
            "status": "success",
            "task_id": task_id,
            "synced_at": datetime.timezone.utc().isoformat(),
        }

    except Exception as exc:
        logger.error(f"Error syncing task {task_id}: {str(exc)}")
        raise self.retry(exc=exc)

    finally:
        db.close()

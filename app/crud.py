# ============================================================
# crud.py
# All database operations live here, keeping route handlers thin.
# Every function receives a SQLAlchemy Session and returns either
# an ORM object, a list, or None (so callers decide on HTTP codes).
# ============================================================

from sqlalchemy.orm import Session

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskPatch


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def create_task(db: Session, task_in: TaskCreate) -> Task:
    """
    Insert a new Task row.

    Parameters
    ----------
    db      : active database session
    task_in : validated Pydantic model from the POST body

    Returns
    -------
    The newly created Task ORM object (with id and created_at filled in).
    """
    task = Task(
        title=task_in.title,
        description=task_in.description or "",
        status=task_in.status or "Pending",
    )
    db.add(task)
    db.commit()
    db.refresh(task)   # reload so created_at is populated
    return task


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_all_tasks(db: Session) -> list[Task]:
    """Return all tasks ordered newest-first."""
    return db.query(Task).order_by(Task.created_at.desc()).all()


def get_task_by_id(db: Session, task_id: int) -> Task | None:
    """Return one task by primary key, or None if not found."""
    return db.query(Task).filter(Task.id == task_id).first()


# ---------------------------------------------------------------------------
# UPDATE (full replace)
# ---------------------------------------------------------------------------

def update_task(db: Session, task_id: int, task_in: TaskUpdate) -> Task | None:
    """
    PUT — replace every mutable field on an existing task.

    Returns the updated Task, or None if task_id does not exist.
    """
    task = get_task_by_id(db, task_id)
    if task is None:
        return None

    task.title = task_in.title
    task.description = task_in.description or ""
    task.status = task_in.status

    db.commit()
    db.refresh(task)
    return task


# ---------------------------------------------------------------------------
# PATCH (partial update — status only)
# ---------------------------------------------------------------------------

def patch_task_status(db: Session, task_id: int, patch_in: TaskPatch) -> Task | None:
    """
    PATCH — update only the status field of an existing task.

    Returns the updated Task, or None if task_id does not exist.
    """
    task = get_task_by_id(db, task_id)
    if task is None:
        return None

    task.status = patch_in.status

    db.commit()
    db.refresh(task)
    return task


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def delete_task(db: Session, task_id: int) -> bool:
    """
    Delete a task by ID.

    Returns True if deleted, False if the task did not exist.
    """
    task = get_task_by_id(db, task_id)
    if task is None:
        return False

    db.delete(task)
    db.commit()
    return True

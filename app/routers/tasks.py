# ============================================================
# routers/tasks.py
# All HTTP endpoints for Task CRUD operations.
# Methods covered: GET, POST, PUT, PATCH, DELETE
# ============================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.schemas import APIResponse, TaskCreate, TaskOut, TaskPatch, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ---------------------------------------------------------------------------
# POST /tasks  — Create a new task
# ---------------------------------------------------------------------------

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=APIResponse,
    summary="Create a new task",
)
def create_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    """
    **POST /tasks**

    Creates a brand-new task.

    - **title** is required (1–200 characters)
    - **description** is optional
    - **status** defaults to *Pending*
    """
    task = crud.create_task(db, task_in)
    return APIResponse(
        success=True,
        message="Task created successfully",
        data=TaskOut.model_validate(task),
    )


# ---------------------------------------------------------------------------
# GET /tasks  — Retrieve all tasks
# ---------------------------------------------------------------------------

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
    summary="Get all tasks",
)
def get_all_tasks(db: Session = Depends(get_db)):
    """
    **GET /tasks**

    Returns every task ordered newest-first.
    """
    tasks = crud.get_all_tasks(db)
    data = [TaskOut.model_validate(t) for t in tasks]
    return APIResponse(
        success=True,
        message=f"{len(data)} task(s) found",
        data=data,
    )


# ---------------------------------------------------------------------------
# GET /tasks/{task_id}  — Retrieve one task
# ---------------------------------------------------------------------------

@router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
    summary="Get a task by ID",
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    **GET /tasks/{task_id}**

    Returns a single task. Raises **404** if not found.
    """
    task = crud.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} not found",
        )
    return APIResponse(
        success=True,
        message="Task retrieved successfully",
        data=TaskOut.model_validate(task),
    )


# ---------------------------------------------------------------------------
# PUT /tasks/{task_id}  — Full update
# ---------------------------------------------------------------------------

@router.put(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
    summary="Fully update a task (replace all fields)",
)
def update_task(task_id: int, task_in: TaskUpdate, db: Session = Depends(get_db)):
    """
    **PUT /tasks/{task_id}**

    Replaces **all** mutable fields of an existing task.
    All fields must be supplied. Raises **404** if the task does not exist.
    """
    task = crud.update_task(db, task_id, task_in)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} not found",
        )
    return APIResponse(
        success=True,
        message="Task updated successfully",
        data=TaskOut.model_validate(task),
    )


# ---------------------------------------------------------------------------
# PATCH /tasks/{task_id}  — Partial update (status only)
# ---------------------------------------------------------------------------

@router.patch(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
    summary="Update only the status of a task",
)
def patch_task(task_id: int, patch_in: TaskPatch, db: Session = Depends(get_db)):
    """
    **PATCH /tasks/{task_id}**

    Updates **only** the `status` field (*Pending* → *Completed* or vice-versa).
    Raises **404** if the task does not exist.
    """
    task = crud.patch_task_status(db, task_id, patch_in)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} not found",
        )
    return APIResponse(
        success=True,
        message="Task status updated successfully",
        data=TaskOut.model_validate(task),
    )


# ---------------------------------------------------------------------------
# DELETE /tasks/{task_id}  — Delete a task
# ---------------------------------------------------------------------------

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=APIResponse,
    summary="Delete a task",
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    **DELETE /tasks/{task_id}**

    Permanently removes a task. Raises **404** if the task does not exist.
    """
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} not found",
        )
    return APIResponse(
        success=True,
        message="Task deleted successfully",
        data=None,
    )

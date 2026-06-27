# Task Manager — FastAPI CRUD Application

A complete, production-quality Task Manager built with **FastAPI**, **SQLAlchemy**, and a **Vanilla JS** frontend. This project demonstrates all five HTTP methods (GET, POST, PUT, PATCH, DELETE) through a clean REST API.

---

## Project Overview

| Layer    | Technology                       |
|----------|----------------------------------|
| Backend  | FastAPI, SQLAlchemy ORM, SQLite  |
| Schemas  | Pydantic v2                      |
| Server   | Uvicorn (ASGI)                   |
| Frontend | HTML, CSS, Vanilla JS (Fetch API)|
| Database | SQLite (`tasks.db`)              |

---

## Folder Structure

```
task-manager/
│
├── app/
│   ├── __init__.py      # package marker
│   ├── main.py          # FastAPI app factory, middleware, startup
│   ├── database.py      # SQLAlchemy engine + session dependency
│   ├── models.py        # ORM model: Task table
│   ├── schemas.py       # Pydantic request/response models
│   ├── crud.py          # All database operations (no SQL in routes)
│   │
│   └── routers/
│       ├── __init__.py
│       └── tasks.py     # Route handlers for every CRUD endpoint
│
├── templates/
│   └── index.html       # Single-page frontend (served by Jinja2)
│
├── static/
│   ├── style.css        # Responsive light-theme UI
│   └── app.js           # All Fetch API calls
│
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.10+
- pip

---

## Installation & Setup

```bash
# 1. Clone / extract the project
cd task-manager

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## How to Run

```bash
# From the task-manager/ directory (where app/ lives):
uvicorn app.main:app --reload
```

Then open your browser:

| URL                          | Description               |
|------------------------------|---------------------------|
| http://localhost:8000        | Task Manager UI           |
| http://localhost:8000/docs   | Swagger UI (interactive)  |
| http://localhost:8000/redoc  | ReDoc documentation       |
| http://localhost:8000/health | Health check endpoint     |

> **Note:** `tasks.db` is created automatically in the working directory on first run.

---

## API Endpoints

| Method | Path            | Description                        | HTTP Code |
|--------|-----------------|------------------------------------|-----------|
| POST   | `/tasks`        | Create a new task                  | 201       |
| GET    | `/tasks`        | Get all tasks (newest first)       | 200       |
| GET    | `/tasks/{id}`   | Get a single task by ID            | 200 / 404 |
| PUT    | `/tasks/{id}`   | Full update (replace all fields)   | 200 / 404 |
| PATCH  | `/tasks/{id}`   | Partial update (status only)       | 200 / 404 |
| DELETE | `/tasks/{id}`   | Delete a task                      | 200 / 404 |

### Uniform response format

```json
{
  "success": true,
  "message": "Task created successfully",
  "data": {
    "id": 1,
    "title": "Review PR",
    "description": "Check the authentication PR",
    "status": "Pending",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### Request body examples

**POST / PUT**
```json
{
  "title": "Review PR",
  "description": "Check the authentication PR",
  "status": "Pending"
}
```

**PATCH**
```json
{ "status": "Completed" }
```

---

## Status Codes Returned

| Code | Meaning                           |
|------|-----------------------------------|
| 200  | OK                                |
| 201  | Created                           |
| 400  | Validation error (bad request)    |
| 404  | Task not found                    |
| 422  | Unprocessable entity (Pydantic)   |
| 500  | Internal server / database error  |

---

## Screenshots

> _Add screenshots of the UI and Swagger docs here._

---

## How Each CRUD Operation Works

1. **POST /tasks** → `TaskCreate` schema validated → `crud.create_task()` inserts row → returns `TaskOut`
2. **GET /tasks** → `crud.get_all_tasks()` queries all rows → returns list of `TaskOut`
3. **GET /tasks/{id}** → `crud.get_task_by_id()` → 404 if missing
4. **PUT /tasks/{id}** → `TaskUpdate` schema → `crud.update_task()` replaces all fields
5. **PATCH /tasks/{id}** → `TaskPatch` schema (status only) → `crud.patch_task_status()`
6. **DELETE /tasks/{id}** → `crud.delete_task()` → 404 if missing, else deletes and returns success

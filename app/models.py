# ============================================================
# models.py
# SQLAlchemy ORM model — maps the `tasks` table in SQLite.
# ============================================================

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Task(Base):
    """
    ORM model for a single task row.

    Columns
    -------
    id          : auto-increment primary key
    title       : short task name (required, max 200 chars)
    description : longer notes (optional)
    status      : "Pending" or "Completed"
    created_at  : set automatically to UTC now on INSERT
    """

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True, default="")
    status = Column(String(20), nullable=False, default="Pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

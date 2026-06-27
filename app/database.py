# ============================================================
# database.py
# SQLAlchemy engine, session factory, and Base declaration.
# Every other module imports `SessionLocal` and `Base` from here.
# ============================================================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite file stored in the project root
DATABASE_URL = "sqlite:///./tasks.db"

# connect_args required only for SQLite — disables same-thread check
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Each request gets its own session, closed when the request ends
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# All ORM models inherit from this Base
Base = declarative_base()


# ---------------------------------------------------------------------------
# Dependency: yields a DB session to route handlers, then closes it cleanly
# ---------------------------------------------------------------------------
def get_db():
    """
    FastAPI dependency injected into route handlers via `Depends(get_db)`.
    Yields one database session per request and guarantees it is closed
    even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

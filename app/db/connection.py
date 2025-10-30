import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine
engine = create_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False, future=True)

# Base class for declarative models
Base = declarative_base()

def get_session() -> Generator:
    """
    Provide a transactional scope around a series of operations.
    Use as:
        with get_session() as session:
            ...
    Or as a FastAPI dependency:
        def endpoint(session = Depends(get_session)):
            ...
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
"""
User Service Layer
-------------------
Handles all business logic related to Users:
- Signup, Authentication, Profile updates
- Auto-create wallet on signup
- Rate limiting & basic security checks
"""

from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from ..db.crud import user_crud, wallet_crud
from ..schemas.user_schema import UserCreate, UserUpdate
from ..core.security import verify_password, get_password_hash
from .wallet_service import create_wallet

# ---- Rate limiting store (basic in-memory, for demo) ----
rate_limit_cache = {}

def rate_limit_check(key: str, limit: int = 5, window_seconds: int = 60):
    """
    Simple rate limiter: allows up to `limit` requests per `window_seconds` per user key.
    Raises 429 Too Many Requests if exceeded.
    """
    now = datetime.utcnow()
    records = rate_limit_cache.get(key, [])
    records = [r for r in records if (now - r) < timedelta(seconds=window_seconds)]

    if len(records) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )

    records.append(now)
    rate_limit_cache[key] = records


# ------------------ SERVICE FUNCTIONS ------------------ #

def create_user(db: Session, user_in: UserCreate):
    """Registers a new user and automatically creates a wallet."""
    rate_limit_check(user_in.email)  # anti-bot / spam signup limiter

    existing_user = user_crud.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = get_password_hash(user_in.password)
    new_user = user_crud.create_user(db, user_in, hashed_pw)

    # Auto-create wallet for the user
    create_wallet(db=db, user_id=new_user.id)

    return new_user


def authenticate_user(db: Session, email: str, password: str):
    """Authenticates user login."""
    rate_limit_check(email)  # prevents brute-force login attempts

    user = user_crud.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return user


def get_user_profile(db: Session, user_id: int):
    """Fetch user details (with wallet info optionally attached)."""
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user_info(db: Session, user_id: int, user_update: UserUpdate):
    """Update user details partially."""
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user_crud.update_user(db, user, user_update)


def delete_user(db: Session, user_id: int):
    """Delete a user and their related wallet + transactions."""
    user = user_crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Optional: cascade deletion logic here
    return user_crud.delete_user(db, user_id)
from sqlalchemy.orm import Session
from app.db.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import get_password_hash


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user with hashed password.
    """
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_email(db: Session, email: str) -> User | None:
    """
    Fetch a user by email.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Fetch a user by ID.
    """
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user: User, updates: UserUpdate) -> User:
    """
    Update user fields selectively.
    """
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user
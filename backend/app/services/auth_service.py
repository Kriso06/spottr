from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.schemas.auth import RegisterRequest


class UserAlreadyExistsError(Exception):
    pass


def register_user(db: Session, register_data: RegisterRequest) -> User:
    username = register_data.username.strip().lower()
    email = str(register_data.email).strip().lower()

    existing_email = db.scalar(
        select(User).where(User.email == email)
    )
    if existing_email is not None:
        raise UserAlreadyExistsError(
            "An account with this email already exists."
        )

    existing_username = db.scalar(
        select(User).where(User.username == username)
    )
    if existing_username is not None:
        raise UserAlreadyExistsError(
            "This username is already taken."
        )

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(register_data.password),
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as error:
        db.rollback()
        raise UserAlreadyExistsError(
            "A user with this email or username already exists."
        ) from error

    return user
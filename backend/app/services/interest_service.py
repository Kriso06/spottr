from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interest import Interest


def list_interests(db: Session) -> list[Interest]:
    statement = select(Interest).order_by(
        Interest.category,
        Interest.name,
    )

    return list(db.scalars(statement).all())
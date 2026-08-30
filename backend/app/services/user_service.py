from sqlalchemy import delete, insert, select
from sqlalchemy.orm import Session

from app.models.interest import Interest, user_interests
from app.models.user import User
from app.schemas.user import (
    ProfileUpdateRequest,
    UserInterestsUpdateRequest,
)


class InvalidInterestIdsError(Exception):
    def __init__(self, invalid_ids: list[int]):
        self.invalid_ids = invalid_ids
        super().__init__("One or more interest IDs do not exist.")


def update_profile(
    db: Session,
    user: User,
    profile_data: ProfileUpdateRequest,
) -> User:
    update_data = profile_data.model_dump(exclude_unset=True)

    if "bio" in update_data:
        user.bio = update_data["bio"]

    db.commit()
    db.refresh(user)

    return user


def get_user_interests(
    db: Session,
    user: User,
) -> list[Interest]:
    statement = (
        select(Interest)
        .join(
            user_interests,
            Interest.id == user_interests.c.interest_id,
        )
        .where(user_interests.c.user_id == user.id)
        .order_by(Interest.category, Interest.name)
    )

    return list(db.scalars(statement).all())


def update_user_interests(
    db: Session,
    user: User,
    interests_data: UserInterestsUpdateRequest,
) -> list[Interest]:
    requested_ids = interests_data.interest_ids

    statement = select(Interest).where(
        Interest.id.in_(requested_ids)
    )
    found_interests = list(db.scalars(statement).all())

    found_ids = {interest.id for interest in found_interests}
    invalid_ids = sorted(set(requested_ids) - found_ids)

    if invalid_ids:
        raise InvalidInterestIdsError(invalid_ids)

    db.execute(
        delete(user_interests).where(
            user_interests.c.user_id == user.id
        )
    )

    db.execute(
        insert(user_interests),
        [
            {
                "user_id": user.id,
                "interest_id": interest_id,
            }
            for interest_id in requested_ids
        ],
    )

    db.commit()

    return get_user_interests(db, user)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import (
    ProfileUpdateRequest,
    UserInterestsResponse,
    UserInterestsUpdateRequest,
)
from app.services.user_service import (
    InvalidInterestIdsError,
    get_user_interests,
    update_profile,
    update_user_interests,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
)
def update_my_profile(
    profile_data: ProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return update_profile(
        db=db,
        user=current_user,
        profile_data=profile_data,
    )


@router.get(
    "/me/interests",
    response_model=UserInterestsResponse,
)
def get_my_interests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserInterestsResponse:
    interests = get_user_interests(
        db=db,
        user=current_user,
    )

    return UserInterestsResponse(interests=interests)


@router.put(
    "/me/interests",
    response_model=UserInterestsResponse,
)
def update_my_interests(
    interests_data: UserInterestsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserInterestsResponse:
    try:
        interests = update_user_interests(
            db=db,
            user=current_user,
            interests_data=interests_data,
        )
    except InvalidInterestIdsError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "invalid_interest_ids",
                "invalid_ids": error.invalid_ids,
            },
        ) from error

    return UserInterestsResponse(interests=interests)
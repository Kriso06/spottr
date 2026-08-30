from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.interest import InterestResponse
from app.services.interest_service import list_interests

router = APIRouter(
    prefix="/interests",
    tags=["Interests"],
)


@router.get(
    "",
    response_model=list[InterestResponse],
)
def get_interests(
    db: Session = Depends(get_db),
) -> list[InterestResponse]:
    return list_interests(db)
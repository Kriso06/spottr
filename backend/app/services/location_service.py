from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.location import (
    LocationResponse,
    LocationUpdateRequest,
)


def update_user_location(
    db: Session,
    user: User,
    location_data: LocationUpdateRequest,
) -> LocationResponse:
    user.last_known_location = WKTElement(
        f"POINT({location_data.longitude} {location_data.latitude})",
        srid=4326,
    )

    db.commit()
    db.refresh(user)

    return LocationResponse(
        latitude=location_data.latitude,
        longitude=location_data.longitude,
    )
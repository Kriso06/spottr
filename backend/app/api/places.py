from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.place import NearbyPlaceResponse
from app.services.place_service import find_nearby_places

router = APIRouter(
    prefix="/places",
    tags=["Places"],
)


@router.get(
    "/nearby",
    response_model=list[NearbyPlaceResponse],
)
def get_nearby_places(
    latitude: float = Query(
        ...,
        ge=-90,
        le=90,
    ),
    longitude: float = Query(
        ...,
        ge=-180,
        le=180,
    ),
    radius_meters: int = Query(
        default=5000,
        ge=100,
        le=20000,
    ),
    category: str | None = Query(
        default=None,
        min_length=1,
        max_length=50,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    db: Session = Depends(get_db),
) -> list[NearbyPlaceResponse]:
    results = find_nearby_places(
        db=db,
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius_meters,
        category=category,
        limit=limit,
    )

    return [
        NearbyPlaceResponse(
            id=place.id,
            osm_id=place.osm_id,
            name=place.name,
            category=place.category,
            address=place.address,
            latitude=place.latitude,
            longitude=place.longitude,
            average_rating=place.average_rating,
            vibe_score=place.vibe_score,
            distance_meters=round(distance, 2),
        )
        for place, distance in results
    ]
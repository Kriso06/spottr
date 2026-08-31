from sqlalchemy import func, select
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

from app.models.place import Place


def find_nearby_places(
    db: Session,
    latitude: float,
    longitude: float,
    radius_meters: int,
    category: str | None,
    limit: int,
) -> list[tuple[Place, float]]:
    user_point = WKTElement(
        f"POINT({longitude} {latitude})",
        srid=4326,
    )

    distance_meters = func.ST_Distance(
        Place.location,
        user_point,
    ).label("distance_meters")

    statement = (
        select(Place, distance_meters)
        .where(
            func.ST_DWithin(
                Place.location,
                user_point,
                radius_meters,
            )
        )
        .order_by(distance_meters)
        .limit(limit)
    )

    if category is not None:
        statement = statement.where(
            Place.category.ilike(category.strip())
        )

    results = db.execute(statement).all()

    return [
        (place, float(distance))
        for place, distance in results
    ]
from pydantic import BaseModel


class NearbyPlaceResponse(BaseModel):
    id: int
    osm_id: str
    name: str
    category: str
    address: str | None
    latitude: float
    longitude: float
    average_rating: float
    vibe_score: float | None
    distance_meters: float
from pydantic import BaseModel, Field


class LocationUpdateRequest(BaseModel):
    latitude: float = Field(
        ge=-90,
        le=90,
    )
    longitude: float = Field(
        ge=-180,
        le=180,
    )


class LocationResponse(BaseModel):
    latitude: float
    longitude: float
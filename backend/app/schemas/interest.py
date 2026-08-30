from pydantic import BaseModel, ConfigDict


class InterestResponse(BaseModel):
    id: int
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)
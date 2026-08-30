from pydantic import BaseModel, Field, field_validator

from app.schemas.interest import InterestResponse


class ProfileUpdateRequest(BaseModel):
    bio: str | None = Field(
        default=None,
        max_length=500,
    )


class UserInterestsUpdateRequest(BaseModel):
    interest_ids: list[int] = Field(
        min_length=1,
        max_length=12,
    )

    @field_validator("interest_ids")
    @classmethod
    def interest_ids_must_be_unique(
        cls,
        interest_ids: list[int],
    ) -> list[int]:
        if len(interest_ids) != len(set(interest_ids)):
            raise ValueError("Interest IDs must not contain duplicates.")

        return interest_ids


class UserInterestsResponse(BaseModel):
    interests: list[InterestResponse]
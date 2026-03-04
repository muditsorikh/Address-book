from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):

    street: str = Field(..., min_length=1, max_length=255, examples=["15 MG Road"])
    city: str = Field(..., min_length=1, max_length=100, examples=["Bangalore"])
    state: str = Field(..., min_length=1, max_length=100, examples=["Karnataka"])
    zip_code: str = Field(..., min_length=1, max_length=20, examples=["560001"])
    country: str = Field(..., min_length=1, max_length=100, examples=["India"])
    latitude: float = Field(
        ..., ge=-90.0, le=90.0,
        description="Latitude (-90 to 90)",
        examples=[12.9716],
    )
    longitude: float = Field(
        ..., ge=-180.0, le=180.0,
        description="Longitude (-180 to 180)",
        examples=[77.5946],
    )


class AddressUpdate(BaseModel):

    street: Optional[str] = Field(None, min_length=1, max_length=255)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    zip_code: Optional[str] = Field(None, min_length=1, max_length=20)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)


class AddressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    street: str
    city: str
    state: str
    zip_code: str
    country: str
    latitude: float
    longitude: float

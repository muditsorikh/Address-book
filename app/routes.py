from __future__ import annotations
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import crud, geo
from app.database import get_db
from app.schemas import AddressCreate, AddressResponse, AddressUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/addresses", tags=["Addresses"])


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(payload: AddressCreate, db: Session = Depends(get_db)):
    logger.info("Creating address in %s, %s", payload.city, payload.country)
    try:
        return crud.create_address(db, payload)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while creating address.")


@router.get("/", response_model=list[AddressResponse])
def list_addresses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    logger.info("Listing addresses skip=%d limit=%d", skip, limit)
    return crud.get_addresses(db, skip=skip, limit=limit)


@router.get("/nearby", summary="Find addresses within a distance")
def nearby_addresses(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    distance_km: float = Query(..., gt=0, description="Search radius in km"),
    db: Session = Depends(get_db),
):
    """Returns addresses within the given radius, sorted by distance."""
    logger.info("Nearby search at (%.4f, %.4f), radius=%.1fkm", latitude, longitude, distance_km)
    return geo.find_nearby(db, latitude, longitude, distance_km)


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(address_id: int, db: Session = Depends(get_db)):
    logger.info("Getting address id=%d", address_id)
    address = crud.get_address(db, address_id)
    if not address:
        logger.warning("Address id=%d not found", address_id)
        raise HTTPException(status_code=404, detail=f"Address {address_id} not found.")
    return address


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, payload: AddressUpdate, db: Session = Depends(get_db)):
    logger.info("Updating address id=%d", address_id)
    try:
        address = crud.update_address(db, address_id, payload)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while updating address.")
    if not address:
        logger.warning("Address id=%d not found for update", address_id)
        raise HTTPException(status_code=404, detail=f"Address {address_id} not found.")
    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    logger.info("Deleting address id=%d", address_id)
    try:
        deleted = crud.delete_address(db, address_id)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error while deleting address.")
    if not deleted:
        logger.warning("Address id=%d not found for deletion", address_id)
        raise HTTPException(status_code=404, detail=f"Address {address_id} not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

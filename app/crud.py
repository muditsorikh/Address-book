from __future__ import annotations
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models import Address
from app.schemas import AddressCreate, AddressUpdate

logger = logging.getLogger(__name__)


def create_address(db: Session, data: AddressCreate) -> Address:
    address = Address(**data.model_dump())
    try:
        db.add(address)
        db.commit()
        db.refresh(address)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to create address")
        raise
    logger.info("Created address id=%s in %s, %s", address.id, address.city, address.country)
    return address


def get_address(db: Session, address_id: int) -> Address | None:
    address = db.query(Address).filter(Address.id == address_id).first()
    if not address:
        logger.info("Address id=%s not found", address_id)
    return address


def get_addresses(db: Session, skip: int = 0, limit: int = 100) -> list[Address]:
    addresses = db.query(Address).offset(skip).limit(limit).all()
    logger.debug("Fetched %d addresses (skip=%d, limit=%d)", len(addresses), skip, limit)
    return addresses


def update_address(db: Session, address_id: int, data: AddressUpdate) -> Address | None:
    """Partial update. Only fields present in the request body get changed."""
    address = get_address(db, address_id)
    if not address:
        return None

    update_fields = data.model_dump(exclude_unset=True)
    if not update_fields:
        logger.info("No fields to update for address id=%s", address_id)
        return address

    for key, val in update_fields.items():
        setattr(address, key, val)

    try:
        db.commit()
        db.refresh(address)
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to update address id=%s", address_id)
        raise

    logger.info("Updated address id=%s, fields=%s", address_id, list(update_fields.keys()))
    return address


def delete_address(db: Session, address_id: int) -> bool:
    """Returns True if deleted, False if not found."""
    address = get_address(db, address_id)
    if not address:
        return False

    try:
        db.delete(address)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Failed to delete address id=%s", address_id)
        raise

    logger.info("Deleted address id=%s", address_id)
    return True

from __future__ import annotations
import logging
from geopy.distance import geodesic
from sqlalchemy.orm import Session

from app.models import Address

logger = logging.getLogger(__name__)


def find_nearby(
    db: Session, lat: float, lon: float, radius_km: float
) -> list[dict]:
    origin = (lat, lon)
    addresses = db.query(Address).all()

    results = []
    for addr in addresses:
        dist = geodesic(origin, (addr.latitude, addr.longitude)).kilometers
        if dist <= radius_km:
            results.append({
                "id": addr.id,
                "street": addr.street,
                "city": addr.city,
                "state": addr.state,
                "zip_code": addr.zip_code,
                "country": addr.country,
                "latitude": addr.latitude,
                "longitude": addr.longitude,
                "distance_km": round(dist, 3),
            })

    results.sort(key=lambda x: x["distance_km"])

    logger.info(
        "Nearby search (%.4f, %.4f) r=%.1fkm: %d found",
        lat, lon, radius_km, len(results),
    )
    return results

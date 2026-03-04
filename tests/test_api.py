import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


TEST_DB_URL = "sqlite:///./test_address_book.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def fresh_db():
    """Recreate tables for each test so they don't interfere."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)



BANGALORE = {
    "street": "15 MG Road",
    "city": "Bangalore",
    "state": "Karnataka",
    "zip_code": "560001",
    "country": "India",
    "latitude": 12.9716,
    "longitude": 77.5946,
}

MYSORE = {
    "street": "Sayyaji Rao Road",
    "city": "Mysore",
    "state": "Karnataka",
    "zip_code": "570001",
    "country": "India",
    "latitude": 12.2958,
    "longitude": 76.6394,
}


def _create(addr=BANGALORE):
    """Helper to create an address and return the response json."""
    resp = client.post("/api/v1/addresses/", json=addr)
    assert resp.status_code == 201
    return resp.json()



def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_create_address():
    data = _create()
    assert data["street"] == BANGALORE["street"]
    assert data["latitude"] == BANGALORE["latitude"]
    assert "id" in data


def test_create_rejects_invalid_latitude():
    bad = {**BANGALORE, "latitude": 91.0}
    assert client.post("/api/v1/addresses/", json=bad).status_code == 422


def test_create_rejects_invalid_longitude():
    bad = {**BANGALORE, "longitude": -181.0}
    assert client.post("/api/v1/addresses/", json=bad).status_code == 422


def test_create_rejects_missing_fields():
    resp = client.post("/api/v1/addresses/", json={"street": "X", "city": "Y"})
    assert resp.status_code == 422


def test_create_rejects_empty_street():
    bad = {**BANGALORE, "street": ""}
    assert client.post("/api/v1/addresses/", json=bad).status_code == 422


def test_list_empty():
    resp = client.get("/api/v1/addresses/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_returns_all():
    _create(BANGALORE)
    _create(MYSORE)
    resp = client.get("/api/v1/addresses/")
    assert len(resp.json()) == 2


def test_list_pagination():
    _create(BANGALORE)
    _create(MYSORE)
    resp = client.get("/api/v1/addresses/?skip=0&limit=1")
    assert len(resp.json()) == 1


def test_get_by_id():
    created = _create()
    resp = client.get(f"/api/v1/addresses/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_not_found():
    assert client.get("/api/v1/addresses/9999").status_code == 404


def test_update_partial():
    created = _create()
    resp = client.put(
        f"/api/v1/addresses/{created['id']}",
        json={"city": "Chennai"},
    )
    assert resp.status_code == 200
    assert resp.json()["city"] == "Chennai"
    assert resp.json()["street"] == BANGALORE["street"]  


def test_update_not_found():
    resp = client.put("/api/v1/addresses/9999", json={"city": "X"})
    assert resp.status_code == 404


def test_update_rejects_bad_coords():
    created = _create()
    resp = client.put(
        f"/api/v1/addresses/{created['id']}",
        json={"latitude": 100.0},
    )
    assert resp.status_code == 422


def test_delete():
    created = _create()
    resp = client.delete(f"/api/v1/addresses/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/api/v1/addresses/{created['id']}").status_code == 404


def test_delete_not_found():
    assert client.delete("/api/v1/addresses/9999").status_code == 404


def test_nearby_small_radius():
    """Bangalore and Mysore are ~145km apart, 10km radius should only get Bangalore."""
    _create(BANGALORE)
    _create(MYSORE)

    resp = client.get("/api/v1/addresses/nearby", params={
        "latitude": 12.9716, "longitude": 77.5946, "distance_km": 10,
    })
    data = resp.json()
    assert len(data) == 1
    assert data[0]["city"] == "Bangalore"
    assert "distance_km" in data[0]


def test_nearby_large_radius():
    """200km from Bangalore should include both cities."""
    _create(BANGALORE)
    _create(MYSORE)

    resp = client.get("/api/v1/addresses/nearby", params={
        "latitude": 12.9716, "longitude": 77.5946, "distance_km": 200,
    })
    data = resp.json()
    assert len(data) == 2
    assert data[0]["distance_km"] <= data[1]["distance_km"]


def test_nearby_no_match():
    _create(BANGALORE)
    resp = client.get("/api/v1/addresses/nearby", params={
        "latitude": -33.8688, "longitude": 151.2093, "distance_km": 1,
    })
    assert resp.json() == []


def test_nearby_rejects_invalid_coords():
    resp = client.get("/api/v1/addresses/nearby", params={
        "latitude": 91, "longitude": 0, "distance_km": 10,
    })
    assert resp.status_code == 422


def test_nearby_requires_all_params():
    assert client.get("/api/v1/addresses/nearby").status_code == 422

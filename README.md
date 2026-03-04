# Address Book API

This is an address book REST API built with FastAPI. It stores addresses (with lat/long coordinates) in SQLite, and lets you search for addresses within a given distance from any point.

Built as part of the EastVantage Python assignment.

## How to run

You'll need Python 3.9 or higher. The steps below should work on macOS/Linux. On Windows, use `venv\Scripts\activate` instead of `source`.

**1. Clone and cd into the project:**

```bash
git clone <repository-url>
cd eastvantage
```

**2. Set up a virtual environment and install dependencies:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. Start the server:**

```bash
uvicorn app.main:app --reload
```

That's it. The app runs at http://127.0.0.1:8000. The database file (`address_book.db`) gets created automatically on first run.

**4. Open Swagger UI to try things out:**

Go to http://127.0.0.1:8000/docs in your browser. You can test all the endpoints from there without needing curl or Postman.

## Running the tests

```bash
pip install pytest httpx
pytest -v
```

Tests use a separate SQLite file so they won't touch your actual data.

## Docker (optional)

If you prefer running it in a container:

```bash
docker build -t address-book .
docker run -p 8000:8000 address-book
```

## Endpoints

Base path for all address operations: `/api/v1/addresses/`

| Method | Path | What it does |
|--------|------|--------------|
| POST | `/api/v1/addresses/` | Create a new address |
| GET | `/api/v1/addresses/` | List all addresses (`skip` & `limit` supported) |
| GET | `/api/v1/addresses/{id}` | Get a specific address |
| PUT | `/api/v1/addresses/{id}` | Update an address (partial, only send fields you want to change) |
| DELETE | `/api/v1/addresses/{id}` | Delete an address |
| GET | `/api/v1/addresses/nearby` | Find addresses within a radius |
| GET | `/health` | Health check |

### Quick examples with curl

**Create an address:**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/addresses/ \
  -H "Content-Type: application/json" \
  -d '{
    "street": "15 MG Road",
    "city": "Bangalore",
    "state": "Karnataka",
    "zip_code": "560001",
    "country": "India",
    "latitude": 12.9716,
    "longitude": 77.5946
  }'
```

**Find addresses within 50km of a point:**

```bash
curl "http://127.0.0.1:8000/api/v1/addresses/nearby?latitude=12.97&longitude=77.59&distance_km=50"
```

**Update just the city:**

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/addresses/1 \
  -H "Content-Type: application/json" \
  -d '{"city": "Mysore"}'
```

## Project structure

```
app/
├── config.py      Settings (loaded from env vars)
├── database.py    SQLAlchemy engine & session setup
├── models.py      ORM model for the addresses table
├── schemas.py     Pydantic schemas for validation
├── crud.py        DB operations (create/read/update/delete)
├── geo.py         Nearby search using geopy
├── routes.py      FastAPI route handlers
└── main.py        App entrypoint, logging, error handlers
tests/
└── test_api.py    21 tests covering all endpoints
```

## Configuration

Settings can be overridden with environment variables (prefixed with `ADDRESSBOOK_`), or by creating a `.env` file in the project root.

| Variable | Default | Description |
|----------|---------|-------------|
| `ADDRESSBOOK_DATABASE_URL` | `sqlite:///./address_book.db` | Database connection string |
| `ADDRESSBOOK_LOG_LEVEL` | `INFO` | Logging level |
| `ADDRESSBOOK_DEBUG` | `false` | Turns on SQLAlchemy query logging |

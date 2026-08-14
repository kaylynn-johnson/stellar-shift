import os
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "planets.duckdb"
DB_PATH = Path(os.getenv("DB_PATH", str(DEFAULT_DB_PATH)))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

REFRESH_CRON = os.getenv("REFRESH_CRON", "0 6 * * 1")

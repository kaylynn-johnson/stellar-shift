import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

_TEST_TMP_DIR = Path(tempfile.mkdtemp(prefix="stellar-shift-test-"))

# these must be set before `backend.config` (and anything that imports it) is
# first imported, since it reads them at module-import time
os.environ["DB_PATH"] = str(_TEST_TMP_DIR / "unused.duckdb")
os.environ["CORS_ORIGINS"] = "http://localhost:3000"
os.environ["REFRESH_CRON"] = "0 0 1 1 *"  # once a year -- won't fire during a test run

from backend import ingest  # noqa: E402  (import must follow the env var setup above)


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(_TEST_TMP_DIR, ignore_errors=True)


def make_sample_planets_df() -> pd.DataFrame:
    """A small dataset shaped like the raw NASA TAP response, covering the edge cases
        clean_df/calc_in_habitable_zone need to handle: a planet in the habitable zone,
        one outside it, a missing luminosity that gets backfilled, and a row missing
        required identifiers that clean_df should drop."""
    return pd.DataFrame([
        # in the habitable zone
        {"pl_name": "Test-1 b", "hostname": "Test-1", "sy_snum": 1, "sy_pnum": 1,
         "discoverymethod": "Transit", "disc_year": 2020, "disc_facility": "TestScope",
         "pl_orbper": 300.0, "pl_orbsmax": 1.0, "pl_rade": 1.0, "pl_masse": 1.0,
         "pl_eqt": 288.0, "st_teff": 5778.0, "st_lum": 0.0, "st_mass": 1.0, "st_rad": 1.0,
         "sy_dist": 10.0, "ra": 100.0, "dec": 20.0, "sy_vmag": 8.0},
        # not in the habitable zone (too close to its star)
        {"pl_name": "Test-2 b", "hostname": "Test-2", "sy_snum": 1, "sy_pnum": 1,
         "discoverymethod": "Transit", "disc_year": 2021, "disc_facility": "TestScope",
         "pl_orbper": 3.0, "pl_orbsmax": 0.02, "pl_rade": 2.0, "pl_masse": 5.0,
         "pl_eqt": 1500.0, "st_teff": 5500.0, "st_lum": -0.1, "st_mass": 0.9, "st_rad": 0.9,
         "sy_dist": 20.0, "ra": 110.0, "dec": -10.0, "sy_vmag": 10.0},
        # missing luminosity -- should be backfilled via Stefan-Boltzmann; teff 6000 -> "F"
        {"pl_name": "Test-3 b", "hostname": "Test-3", "sy_snum": 2, "sy_pnum": 3,
         "discoverymethod": "Radial Velocity", "disc_year": 2022, "disc_facility": "TestScope",
         "pl_orbper": 100.0, "pl_orbsmax": 0.5, "pl_rade": 3.0, "pl_masse": None,
         "pl_eqt": None, "st_teff": 6000.0, "st_lum": None, "st_mass": 1.1, "st_rad": 1.05,
         "sy_dist": 30.0, "ra": 120.0, "dec": 30.0, "sy_vmag": 9.5},
        # missing identifiers -- clean_df should drop this row entirely
        {"pl_name": None, "hostname": None, "sy_snum": 1, "sy_pnum": 1,
         "discoverymethod": "Transit", "disc_year": 2019, "disc_facility": "TestScope",
         "pl_orbper": 50.0, "pl_orbsmax": 0.3, "pl_rade": 1.5, "pl_masse": 2.0,
         "pl_eqt": 400.0, "st_teff": 5000.0, "st_lum": -0.2, "st_mass": 0.8, "st_rad": 0.8,
         "sy_dist": 40.0, "ra": 130.0, "dec": 40.0, "sy_vmag": 11.0},
    ])


def build_fixture_db(path, day=1) -> Path:
    """cleans the sample dataset and writes it to a real duckdb file via the
        production write_duckdb() code path, so tests exercise real behavior"""
    df = ingest.clean_df(make_sample_planets_df())
    ingest.write_duckdb(df, path, datetime(2026, 1, day, tzinfo=timezone.utc))
    return path


@pytest.fixture
def seeded_db_path(tmp_path):
    return build_fixture_db(tmp_path / "seeded.duckdb")


@pytest.fixture
def client(seeded_db_path, monkeypatch):
    """a TestClient wired up against the seeded fixture database, running the app's
        real lifespan (startup finds the db already present, so it skips the
        network-bootstrap path and never talks to the real NASA API)"""
    monkeypatch.setattr("backend.config.DB_PATH", seeded_db_path)
    from starlette.testclient import TestClient

    from backend.main import app

    with TestClient(app) as test_client:
        yield test_client

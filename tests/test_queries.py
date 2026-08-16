import os

from backend import queries
from conftest import build_fixture_db


def test_all_planets_excludes_row_dropped_by_clean_df(tmp_path):
    path = build_fixture_db(tmp_path / "a.duckdb")
    queries.init_connection(db_path=path)
    try:
        planets = queries.all_planets()
        names = {p["pl_name"] for p in planets}
        assert names == {"Test-1 b", "Test-2 b", "Test-3 b"}
    finally:
        queries.close_connection()


def test_habitable_zone_flag(tmp_path):
    path = build_fixture_db(tmp_path / "b.duckdb")
    queries.init_connection(db_path=path)
    try:
        hz = {p["pl_name"]: p["in_hz"] for p in queries.habitable_planets()}
        assert hz["Test-1 b"] == 1
        assert hz["Test-2 b"] == 0
    finally:
        queries.close_connection()


def test_planet_id_lookup(tmp_path):
    path = build_fixture_db(tmp_path / "c.duckdb")
    queries.init_connection(db_path=path)
    try:
        assert queries.planet_id("Test-1 b")[0]["pl_name"] == "Test-1 b"
        assert queries.planet_id("nonexistent planet") == []
    finally:
        queries.close_connection()


def test_search_filters_by_spectral_type(tmp_path):
    path = build_fixture_db(tmp_path / "d.duckdb")
    queries.init_connection(db_path=path)
    try:
        results = queries.search_planets(
            filters={
                "radius_min": None, "radius_max": None,
                "orbit_period_min": None, "orbit_period_max": None,
                "discovery_method": None, "spectral_type": "F",
            },
            limit=25, offset=0,
        )
        # only Test-3 b has st_teff=6000, which classifies as spectral type F
        assert results["total"] == 1
        assert {r["pl_name"] for r in results["results"]} == {"Test-3 b"}
    finally:
        queries.close_connection()


def test_get_last_refreshed_matches_write_time(tmp_path):
    path = build_fixture_db(tmp_path / "e.duckdb", day=5)
    queries.init_connection(db_path=path)
    try:
        assert queries.get_last_refreshed() == "2026-01-05T00:00:00+00:00"
    finally:
        queries.close_connection()


def test_refresh_connection_reads_replaced_file_not_stale_cache(tmp_path):
    """Regression test for a real bug: refresh_connection() must see the *new* file
        contents after an atomic os.replace(), not a cached in-memory instance of the
        old one. This broke in production once already because the old connection was
        closed *after* opening the new one instead of before -- DuckDB shares one
        in-memory database instance per file path per process, so opening a "new"
        connection while the old one is still attached just reattaches to the stale
        instance."""
    live_path = tmp_path / "live.duckdb"
    build_fixture_db(live_path, day=1)
    queries.init_connection(db_path=live_path)
    try:
        assert queries.get_last_refreshed() == "2026-01-01T00:00:00+00:00"

        # simulate a weekly refresh: build the new data elsewhere, then atomically
        # swap it into the live path, exactly like ingest.refresh_database() does
        tmp_new_path = tmp_path / "live.duckdb.tmp"
        build_fixture_db(tmp_new_path, day=2)
        os.replace(tmp_new_path, live_path)

        queries.refresh_connection(db_path=live_path)
        assert queries.get_last_refreshed() == "2026-01-02T00:00:00+00:00"
    finally:
        queries.close_connection()

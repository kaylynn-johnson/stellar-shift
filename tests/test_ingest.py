from backend import ingest
from conftest import make_sample_planets_df


def test_refresh_database_swaps_in_new_file_on_validation_pass(tmp_path, monkeypatch):
    db_path = tmp_path / "live.duckdb"

    monkeypatch.setattr(ingest, "query_TAP_planets", lambda: make_sample_planets_df())
    monkeypatch.setattr(ingest, "run_validation", lambda path: True)

    assert ingest.refresh_database(db_path=db_path) is True
    assert db_path.exists()
    assert not (tmp_path / "live.duckdb.tmp").exists()


def test_refresh_database_keeps_old_file_on_validation_fail(tmp_path, monkeypatch):
    """the core safety guarantee: a bad refresh must never touch what's being served"""
    db_path = tmp_path / "live.duckdb"
    db_path.write_bytes(b"old-database-contents")

    monkeypatch.setattr(ingest, "query_TAP_planets", lambda: make_sample_planets_df())
    monkeypatch.setattr(ingest, "run_validation", lambda path: False)

    assert ingest.refresh_database(db_path=db_path) is False
    assert db_path.read_bytes() == b"old-database-contents"
    assert not (tmp_path / "live.duckdb.tmp").exists()


def test_refresh_database_creates_missing_parent_directory(tmp_path, monkeypatch):
    db_path = tmp_path / "nested" / "dir" / "planets.duckdb"

    monkeypatch.setattr(ingest, "query_TAP_planets", lambda: make_sample_planets_df())
    monkeypatch.setattr(ingest, "run_validation", lambda path: True)

    assert ingest.refresh_database(db_path=db_path) is True
    assert db_path.exists()


def test_clean_df_drops_rows_missing_identifiers():
    df = ingest.clean_df(make_sample_planets_df())
    assert df["pl_name"].isna().sum() == 0
    assert len(df) == 3


def test_clean_df_backfills_missing_luminosity():
    df = ingest.clean_df(make_sample_planets_df())
    row = df[df["pl_name"] == "Test-3 b"].iloc[0]
    assert row["st_lum"] is not None
    import math
    assert not math.isnan(row["st_lum"])

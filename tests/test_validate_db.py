import duckdb

from backend import validate_db
from conftest import build_fixture_db


def test_passes_null_name_and_duplicate_checks_on_clean_data(tmp_path, capsys):
    path = build_fixture_db(tmp_path / "clean.duckdb")

    validate_db.run_validation(path)

    out = capsys.readouterr().out
    assert "[PASS] No null planet names: 0" in out
    assert "[PASS] No null hostnames: 0" in out
    assert "[PASS] No duplicate planet names: 0" in out


def test_flags_null_planet_names(tmp_path, capsys):
    path = build_fixture_db(tmp_path / "dirty.duckdb")
    con = duckdb.connect(str(path))
    con.execute("INSERT INTO planets (pl_name) VALUES (NULL)")
    con.close()

    result = validate_db.run_validation(path)

    assert result is False
    out = capsys.readouterr().out
    assert "[FAIL] No null planet names" in out


def test_flags_duplicate_planet_names(tmp_path, capsys):
    path = build_fixture_db(tmp_path / "dupes.duckdb")
    con = duckdb.connect(str(path))
    con.execute("INSERT INTO planets (pl_name, hostname) VALUES ('Test-1 b', 'Test-1')")
    con.close()

    result = validate_db.run_validation(path)

    assert result is False
    out = capsys.readouterr().out
    assert "[FAIL] No duplicate planet names" in out


def test_overall_result_is_false_on_small_fixture(tmp_path):
    """the row-count/volume checks (>5000 rows, >500 recent discoveries, etc.) are
        tuned for the real ~6000-row production dataset and will never pass on a
        small fixture -- this just documents that run_validation()'s aggregate result
        reflects that honestly rather than silently ignoring failing checks"""
    path = build_fixture_db(tmp_path / "small.duckdb")
    assert validate_db.run_validation(path) is False

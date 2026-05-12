import duckdb
from datetime import datetime
from pathlib import Path

DB_FILE = Path(__file__).parent.parent / "data" / "planets.duckdb"

def run_validation():
    CHECKS = [
        ("Total row count", "SELECT COUNT(*) FROM planets", lambda n: n > 5000),
        ("No null planet names", "SELECT COUNT(*) FROM planets WHERE pl_name IS NULL", lambda n: n == 0),
        ("No null hostnames", "SELECT COUNT(*) FROM planets WHERE hostname IS NULL", lambda n: n == 0),
        ("HZ flag added", "SELECT COUNT(*) FROM planets WHERE in_hz != 0 AND in_hz != 1 AND in_hz IS NOT NULL", lambda n: n == 0),
        ("Both HZ flags present", "SELECT COUNT(DISTINCT(in_hz)) FROM planets", lambda n: n == 2),
        ("Unknown HZ planets present", "SELECT COUNT(*) FROM planets WHERE in_hz IS NULL", lambda n: n > 0),
        ("Reasonable radius", "SELECT MAX(pl_rade) FROM planets", lambda n: n < 100),
        ("Reasonable mass", "SELECT MAX(pl_masse) FROM planets", lambda n: n < 5000),
        ("Reasonable orbital period", "SELECT MIN(pl_orbper) FROM planets WHERE pl_orbper IS NOT NULL", lambda n: n > 0),
        ("Reasonable equilibrium temperature", "SELECT MAX(pl_eqt) FROM planets", lambda n: n < 5000),
        ("Reasonable stellar temperature", "SELECT MIN(st_teff) FROM planets WHERE st_teff IS NOT NULL", lambda n: n > 1000),
        ("Reasonable discovery year - early", "SELECT MIN(disc_year) FROM planets", lambda n: n >= 1992),
        ("Reasonable discover year - high", "SELECT MAX(disc_year) FROM planets", lambda n: n <= datetime.now().year),
        ("Recent discoveries present", "SELECT COUNT(*) FROM planets WHERE disc_year >= 2020", lambda n: n > 500),
        ("Reasonable null rate for radius", "SELECT ROUND(100.0 * SUM(CASE WHEN pl_rade IS NULL THEN 1 ELSE 0 END) / COUNT(*), 1) FROM planets", lambda n: n < 30),
        ("Transit is dominate method", "SELECT ROUND(100.0 * SUM(CASE WHEN discoverymethod = 'Transit' THEN 1 ELSE 0 END) / COUNT(*), 1) FROM planets", lambda n: n > 50),
        ("No duplicate planet names", "SELECT COUNT(*) - COUNT(DISTINCT pl_name) FROM planets", lambda n: n == 0),
    ]

    con = duckdb.connect(str(DB_FILE))
    for title, query, check in CHECKS:
        result = con.execute(query).fetchone()[0]
        status = "PASS" if check(result) else "FAIL"
        print(f"[{status}] {title}: {result}")
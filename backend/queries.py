import threading

import duckdb
import pandas as pd
import numpy as np

from . import config

_lock = threading.Lock()
_con = None


def init_connection(db_path=None):
    """opens the read-only connection; must be called once the database file is
        known to exist (see main.py's startup bootstrap)"""
    global _con
    new_con = duckdb.connect(str(db_path or config.DB_PATH), read_only=True)
    with _lock:
        _con = new_con


def refresh_connection(db_path=None):
    """reopens the read-only connection against the (just-swapped) database file.
        DuckDB shares one in-memory instance per file path per process, so the old
        connection must be closed *before* reopening -- otherwise the "new" connection
        just reattaches to the stale instance instead of reading the replaced file."""
    global _con
    with _lock:
        _con.close()
        _con = duckdb.connect(str(db_path or config.DB_PATH), read_only=True)


def close_connection():
    global _con
    with _lock:
        if _con is not None:
            _con.close()
            _con = None


def get_last_refreshed():
    with _lock:
        result = _con.execute("SELECT refreshed_at FROM meta").fetchone()
    return result[0] if result else None


def all_planets():

    all_planets_query = "SELECT pl_name, hostname, sy_snum, sy_pnum, pl_orbper, pl_rade, pl_masse, in_hz FROM planets"

    with _lock:
        result = _con.execute(all_planets_query).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result


def planet_id(id):

    planet_id_query = "SELECT pl_name, hostname, sy_snum, sy_pnum, pl_orbper, pl_rade, pl_masse, in_hz FROM planets WHERE pl_name = ?"

    with _lock:
        result = _con.execute(planet_id_query, [id]).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result


def habitable_planets():

    habitable_planets_query = "SELECT pl_name, in_hz, hz_lower, hz_upper FROM planets"

    with _lock:
        result = _con.execute(habitable_planets_query).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result


def filter_options():

    with _lock:
        methods = _con.execute(
            "SELECT DISTINCT discoverymethod FROM planets ORDER BY 1"
        ).fetchall()
        types = _con.execute(
            "SELECT DISTINCT stellar_category FROM planets WHERE stellar_category IS NOT NULL ORDER BY 1"
        ).fetchall()

    return {
        "discovery_methods": [m[0] for m in methods],
        "spectral_types": [t[0] for t in types]
    }


def search_planets(filters: dict, limit: int, offset: int):

    clauses = []
    parameters = {}

    if filters["radius_min"] is not None:
        clauses.append("pl_rade >= $radius_min")
        parameters["radius_min"] = filters["radius_min"]

    if filters["radius_max"] is not None:
        clauses.append("pl_rade <= $radius_max")
        parameters["radius_max"] = filters["radius_max"]

    if filters["orbit_period_min"] is not None:
        clauses.append("pl_orbper >= $orbit_period_min")
        parameters["orbit_period_min"] = filters["orbit_period_min"]

    if filters["orbit_period_max"] is not None:
        clauses.append("pl_orbper <= $orbit_period_max")
        parameters["orbit_period_max"] = filters["orbit_period_max"]

    if filters["discovery_method"] is not None:
        clauses.append("discoverymethod = $discovery_method")
        parameters["discovery_method"] = filters["discovery_method"]

    if filters["spectral_type"] is not None:
        clauses.append("stellar_category = $spectral_type")
        parameters["spectral_type"] = filters["spectral_type"]

    # last bit is if there are no parameters passed
    where_clause = " AND ".join(clauses) if clauses else "1=1"
   
    with _lock:
        total = _con.execute(
            f"SELECT COUNT(*) FROM planets WHERE {where_clause}", parameters
        ).fetchone()[0]

        search_query = f"SELECT * FROM planets WHERE {where_clause} LIMIT $limit OFFSET $offset"
        parameters["limit"] = limit
        parameters["offset"] = offset
        result = _con.execute(search_query, parameters).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return {"results": result, "total": total}
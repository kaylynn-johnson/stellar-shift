import duckdb
import pandas as pd
import numpy as np
from pathlib import Path

DB_FILE = Path(__file__).parent.parent / "data" / "planets.duckdb"
con = duckdb.connect(str(DB_FILE), read_only=True)

def all_planets():

    all_planets_query = "SELECT pl_name, hostname, sy_snum, sy_pnum, pl_orbper, pl_rade, pl_masse, in_hz FROM planets"

    result = con.execute(all_planets_query).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result


def planet_id(id):

    planet_id_query = "SELECT pl_name, hostname, sy_snum, sy_pnum, pl_orbper, pl_rade, pl_masse, in_hz FROM planets where rowid = ?"

    result = con.execute(planet_id_query, [id]).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result


def habitable_planets():

    habitable_planets_query = "SELECT pl_name, in_hz, hz_lower, hz_upper FROM planets"

    result = con.execute(habitable_planets_query).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result


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
    search_query = f"SELECT * FROM planets WHERE {where_clause} LIMIT $limit OFFSET $offset"
    parameters["limit"] = limit
    parameters["offset"] = offset
    result = con.execute(search_query, parameters).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result
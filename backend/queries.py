import duckdb
import pandas as pd
import numpy as np
from pathlib import Path

DB_FILE = Path(__file__).parent.parent / "data" / "planets.duckdb"

def all_planets():
    con = duckdb.connect(str(DB_FILE))

    all_planets_query = "SELECT pl_name, hostname, sy_snum, sy_pnum, pl_orbper, pl_rade, pl_masse, in_hz FROM planets"

    result = con.execute(all_planets_query).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result


def planet_id(id):
    con = duckdb.connect(str(DB_FILE))

    planet_id_query = "SELECT pl_name, hostname, sy_snum, sy_pnum, pl_orbper, pl_rade, pl_masse, in_hz FROM planets where rowid = ?"

    result = con.execute(planet_id_query, [id]).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result


def habitable_planets():
    con = duckdb.connect(str(DB_FILE))

    habitable_planets_query = "SELECT pl_name, in_hz, hz_lower, hz_upper FROM planets"

    result = con.execute(habitable_planets_query).fetchdf()
    result = result.replace([np.inf, -np.inf, np.nan], None).to_dict(orient="records")

    return result

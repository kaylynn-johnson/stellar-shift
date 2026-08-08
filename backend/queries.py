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

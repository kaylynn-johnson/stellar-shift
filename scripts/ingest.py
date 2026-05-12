import io
import requests
import duckdb
import pandas as pd
from pathlib import Path
from hz_calculator import calc_in_habitable_zone
from validate_db import run_validation

DB_FILE = Path(__file__).parent.parent / "data" / "planets.duckdb"

def query_TAP_planets():
    """queries all the lines from planetary systems table of the NASA Exoplanet Archive
        columns are determined based on default columns that are easily understandable of the planetary systems table"""
    tap_query_columns = ["pl_name",                 # planet name
                         "hostname",                # host name
                         "sy_snum",                 # number of stars in planetary system
                         "sy_pnum",                 # number of planets in planetary system
                         "discoverymethod",         # discovery method
                         "disc_year",               # discovery year
                         "disc_facility",           # discovery facility
                         "pl_orbper",               # orbital period in days
                         "pl_orbsmax",              # orbit semi-major axis in AU
                         "pl_rade",                 # planet radius in Earth radius
                         "pl_masse",                # planet mass in Earth mass
                         "pl_eqt",                  # equilibrium temperature in K
                         "st_teff",                 # stellar effective temperature in K
                         "st_mass",                 # stellar mass in Sun mass
                         "sy_dist",                 # distance from Earth to the planetary system in parsecs
                         "ra",                      # right ascension in decimal degrees
                         "dec",                     # declination in decimal degrees
                         "sy_vmag",                 # brightness of host star using V-band in units of magnitude
                         ]
    response = requests.get(f"https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+{','.join(tap_query_columns)}+from+ps+where+default_flag=1&format=csv")
    if response.status_code != 200:
        raise RuntimeError(f"NASA Exoplanet Archive API request failed: {response.status_code} - {response.text}")
    
    return pd.read_csv(io.StringIO(response.text))


def clean_df(df):
    """cleans the dataframe from the GET request of TAP"""

    # removes rows without planet name or host name
    df = df.dropna(subset=["pl_name", "hostname"])

    # convert K to F
    df["pl_eqt_F"] = round(((df["pl_eqt"] - 273.15) * 1.8) + 32, 2)
    df["st_teff_F"] = round(((df["st_teff"] - 273.15)* 1.8) + 32, 2)

    # add habitable zone flag with [K] temp
    df["in_hz"] = df["pl_eqt"].apply(lambda t: calc_in_habitable_zone(t) if pd.notna(t) else None)

    return df


def write_duckdb(df):
    """write dataframe to a duckdb database in the data folder with name planets.duckdb"""
    con = duckdb.connect(str(DB_FILE))
    
    # plan to rewrite every time this is run so remove existing table
    con.execute("DROP TABLE IF EXISTS planets")

    # create a fresh planets table
    con.execute("""
                    CREATE TABLE planets AS SELECT * FROM df
                """)
    
    # create indexes on planet's name and habitability to query faster
    con.execute("CREATE INDEX idx_name ON planets(pl_name)")
    con.execute("CREATE INDEX idx_hz ON planets(in_hz)")
    
    # close connection
    con.close()


if __name__ == "__main__":
    df = query_TAP_planets()
    df = clean_df(df)
    write_duckdb(df)
    run_validation()

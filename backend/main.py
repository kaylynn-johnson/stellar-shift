from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import queries

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    queries.con.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/planets")
async def get_planets():
    # return all information from planets.duckdb
    planets = queries.all_planets()
    # check result
    if not planets:
        raise HTTPException(status_code=404, detail="No planets found")
    return planets

@app.get("/api/planets/search")
async def search_planets(
    radius_min: int | None = None, 
    radius_max: int | None = None, 
    orbit_period_min: int | None = None, 
    orbit_period_max: int | None = None,
    discovery_method: str | None = None,
    spectral_type: str | None = None,
    limit: int = 25,
    offset: int = 0
):
    filters = {
        "radius_min": radius_min,
        "radius_max": radius_max,
        "orbit_period_min": orbit_period_min,
        "orbit_period_max": orbit_period_max,
        "discovery_method": discovery_method,
        "spectral_type": spectral_type
    }

    planets = queries.search_planets(filters=filters, limit=limit, offset=offset)
    if not planets:
        raise HTTPException(status_code=404, detail="No planets matching that query")

    return planets


@app.get("/api/planets/{id}")
async def get_planet(id: int):
    # return all information on planet ID from planets.duckdb
    planet = queries.planet_id(id)
    # check result
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")
    return planet


@app.get("/api/habitable-zone")
async def get_habitable_zone():
    # return all information on planets in the habitable zone
    habitable_planets = queries.habitable_planets()
    # check result
    if not habitable_planets:
        raise HTTPException(status_code=404, detail="No habitable planets found")
    return habitable_planets

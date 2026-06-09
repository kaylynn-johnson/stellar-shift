from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import queries

app = FastAPI()

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

import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from . import config, ingest, queries

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stellar-shift")


def scheduled_refresh():
    if ingest.refresh_database():
        queries.refresh_connection()
        app.state.last_refreshed = queries.get_last_refreshed()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not config.DB_PATH.exists():
        logger.info("no database found at %s, running initial ingest", config.DB_PATH)
        ingest.refresh_database()

    queries.init_connection()
    app.state.last_refreshed = queries.get_last_refreshed()

    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_refresh, CronTrigger.from_crontab(config.REFRESH_CRON))
    scheduler.start()

    yield

    scheduler.shutdown()
    queries.close_connection()


app = FastAPI(
    title="StellarShift API",
    description="Search thousands of confirmed exoplanets by size, orbit, and host star, "
    "sourced from the NASA Exoplanet Archive and refreshed weekly.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_data_freshness_header(request: Request, call_next):
    response = await call_next(request)
    last_refreshed = getattr(app.state, "last_refreshed", None)
    if last_refreshed is not None:
        response.headers["X-Data-Last-Modified"] = last_refreshed
    return response


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "last_refreshed": getattr(app.state, "last_refreshed", None),
    }


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


@app.get("/api/planets/filter-options")
async def get_filter_options():
    # return all options for discoverymethod and spectral_type
    filters = queries.filter_options()
    
    return filters
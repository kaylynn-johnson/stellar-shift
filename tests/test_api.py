def test_health_reports_seeded_refresh_time(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["last_refreshed"] == "2026-01-01T00:00:00+00:00"


def test_root_redirects_to_docs(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "/docs"


def test_data_freshness_header_present_on_every_response(client):
    resp = client.get("/api/planets")
    assert resp.headers["x-data-last-modified"] == "2026-01-01T00:00:00+00:00"


def test_get_planets(client):
    resp = client.get("/api/planets")
    assert resp.status_code == 200
    names = {p["pl_name"] for p in resp.json()}
    assert names == {"Test-1 b", "Test-2 b", "Test-3 b"}


def test_get_planet_by_id(client):
    resp = client.get("/api/planets/Test-1%20b")
    assert resp.status_code == 200
    assert resp.json()[0]["pl_name"] == "Test-1 b"


def test_get_planet_by_id_not_found(client):
    resp = client.get("/api/planets/999")
    assert resp.status_code == 404


def test_search_by_spectral_type(client):
    resp = client.get("/api/planets/search", params={"spectral_type": "F"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 1
    assert {p["pl_name"] for p in body["results"]} == {"Test-3 b"}


def test_search_no_matches_is_404(client):
    resp = client.get("/api/planets/search", params={"spectral_type": "O"})
    assert resp.status_code == 404


def test_habitable_zone(client):
    resp = client.get("/api/habitable-zone")
    assert resp.status_code == 200
    hz = {p["pl_name"]: p["in_hz"] for p in resp.json()}
    assert hz["Test-1 b"] == 1
    assert hz["Test-2 b"] == 0


def test_cors_allows_configured_origin(client):
    resp = client.options(
        "/api/planets",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_rejects_other_origins(client):
    resp = client.options(
        "/api/planets",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert "access-control-allow-origin" not in resp.headers

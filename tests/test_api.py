from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert data["status"] == "running"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["database"] == "ok"


def test_stations_limit():
    response = client.get("/stations?limit=5")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "stations" in data

    assert data["count"] <= 5
    assert isinstance(data["stations"], list)
    assert len(data["stations"]) <= 5


def test_station_inexistante():
    response = client.get("/stations/STATION_INEXISTANTE")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Station introuvable"


def test_prediction_station_inexistante():
    response = client.get("/predict/STATION_INEXISTANTE")

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Station introuvable"
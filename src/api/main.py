from pathlib import Path
import sqlite3
import pickle

import pandas as pd

from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import time


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "velops_star.db"
MODEL_PATH = PROJECT_ROOT / "models" / "random_forest_model.pkl"

app = FastAPI(
    title="VelOps Paris API",
    description="API de consultation des données VelOps Paris",
    version="1.0.0",
)
REQUEST_COUNT = Counter(
    "velops_api_requests_total",
    "Nombre total de requetes HTTP",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "velops_api_request_duration_seconds",
    "Temps de traitement des requetes HTTP",
    ["method", "endpoint"],
)

@app.middleware("http")
async def prometheus_middleware(request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status_code=response.status_code,
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path,
    ).observe(duration)

    return response

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )

@app.get("/")
def root():
    return {
        "application": "VelOps Paris",
        "status": "running",
    }


@app.get("/health")
def health():
    database_status = "ok" if DB_PATH.exists() else "missing"

    return {
        "status": "ok",
        "database": database_status,
    }


@app.get("/stations")
def get_stations(limit: int = 10):
    limit = max(1, min(limit, 100))

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute(
            """
            SELECT
                station_id,
                nom_station
            FROM dim_station
            ORDER BY nom_station
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return {
        "count": len(rows),
        "stations": [dict(row) for row in rows],
    }
@app.get("/stations/{station_id}")
def get_station(station_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            """
            SELECT
                ds.station_id,
                ds.nom_station,
                f.velos_disponibles,
                f.places_libres,
                da.nom_arrondissement,
                dt.date_complete
            FROM fait_disponibilite AS f
            JOIN dim_station AS ds
                ON f.station_id = ds.station_id
            LEFT JOIN dim_arrondissement AS da
                ON f.arrondissement_id = da.arrondissement_id
            JOIN dim_temps AS dt
                ON f.temps_id = dt.temps_id
            WHERE ds.station_id = ?
            ORDER BY dt.date_complete DESC
            LIMIT 1
            """,
            (station_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Station introuvable",
        )

    return dict(row)
@app.get("/predict/{station_id}")
def predict_station(station_id: str):
    if not MODEL_PATH.exists():
        raise HTTPException(
            status_code=503,
            detail="Modèle de prédiction indisponible",
        )

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute(
            """
            SELECT
                ds.station_id,
                ds.nom_station,
                f.places_libres,
                f.arrondissement_id,
                dt.date_complete
            FROM fait_disponibilite AS f
            JOIN dim_station AS ds
                ON f.station_id = ds.station_id
            JOIN dim_temps AS dt
                ON f.temps_id = dt.temps_id
            WHERE ds.station_id = ?
            ORDER BY dt.date_complete DESC
            LIMIT 1
            """,
            (station_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Station introuvable",
        )

    if row["arrondissement_id"] is None:
        raise HTTPException(
            status_code=422,
            detail="Arrondissement indisponible pour cette station",
        )

    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)

    model = model_data["model"]

    features = pd.DataFrame(
        [
            {
                "places_libres": row["places_libres"],
                "id_arrondissement": row["arrondissement_id"],
            }
        ]
    )

    prediction = float(model.predict(features)[0])
    prediction = max(0.0, prediction)

    return {
        "station_id": row["station_id"],
        "nom_station": row["nom_station"],
        "date_observation": row["date_complete"],
        "places_libres": row["places_libres"],
        "arrondissement_id": row["arrondissement_id"],
        "prediction_velos_disponibles": round(prediction, 2),
        "modele": "RandomForestRegressor",
    }
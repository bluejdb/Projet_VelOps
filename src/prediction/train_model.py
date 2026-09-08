import sqlite3
import pickle
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


# ============================================================
# CONFIGURATION DES CHEMINS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DB_PATH = PROJECT_ROOT / "velops_paris.db"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "random_forest_model.pkl"

print(f"Chargement des données depuis : {DB_PATH}")


# ============================================================
# VÉRIFICATION DE LA BASE
# ============================================================

if not DB_PATH.exists():
    raise FileNotFoundError(
        f"Base SQLite introuvable : {DB_PATH}"
    )


# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================

conn = sqlite3.connect(DB_PATH)

try:
    df = pd.read_sql_query(
        """
        SELECT
            velos_dispo,
            places_libres,
            id_arrondissement
        FROM stations
        """,
        conn
    )
finally:
    conn.close()


if df.empty:
    raise ValueError(
        "La table 'stations' ne contient aucune donnée."
    )

print(f"Nombre d'observations disponibles : {len(df)}")


# ============================================================
# NETTOYAGE
# ============================================================

df = df.dropna(
    subset=[
        "velos_dispo",
        "places_libres",
        "id_arrondissement"
    ]
)

target = "velos_dispo"

features = [
    "places_libres",
    "id_arrondissement"
]

X = df[features]
y = df[target]


# ============================================================
# SÉPARATION TRAIN / TEST
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print(f"Données d'entraînement : {len(X_train)}")
print(f"Données de test : {len(X_test)}")


# ============================================================
# ENTRAÎNEMENT RANDOM FOREST
# ============================================================

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)


# ============================================================
# ÉVALUATION
# ============================================================

predictions = model.predict(X_test)

mae = mean_absolute_error(
    y_test,
    predictions
)

mse = mean_squared_error(
    y_test,
    predictions
)

rmse = mse ** 0.5

r2 = r2_score(
    y_test,
    predictions
)

print("\n=== ÉVALUATION DU MODÈLE ===")
print(f"MAE  : {mae:.3f}")
print(f"RMSE : {rmse:.3f}")
print(f"R²   : {r2:.3f}")


# ============================================================
# SAUVEGARDE DU MODÈLE
# ============================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

with open(MODEL_PATH, "wb") as f:
    pickle.dump(
        {
            "model": model,
            "features": features,
            "target": target
        },
        f
    )

print(
    f"\nModèle sauvegardé avec succès : {MODEL_PATH}"
)

print("\n=== FIN DE L'ENTRAÎNEMENT ===")
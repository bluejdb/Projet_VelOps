import os
import sqlite3

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
)
from sklearn.metrics import mean_absolute_error, r2_score


# ============================================================
# CHARGEMENT DES DONNEES
# ============================================================

def charger_donnees_historiques():
    """
    Extrait les données des stations depuis la base SQLite
    située à la racine du projet.
    """

    db_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "velops_paris.db",
        )
    )

    if not os.path.exists(db_path):
        print(
            f"[ERREUR] Base de données introuvable : {db_path}"
        )
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)

    try:
        query = """
            SELECT
                s.id,
                s.nom,
                s.velos_dispo,
                s.places_libres,
                a.nom AS arrondissement,
                s.date_ingestion
            FROM stations s
            INNER JOIN arrondissements a
                ON s.id_arrondissement = a.id_arrondissement
        """

        df = pd.read_sql_query(
            query,
            conn,
        )

    finally:
        conn.close()

    return df


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def feature_engineering(df):
    """
    Prépare les variables utilisées par les modèles ML.
    """

    df = df.copy()

    df["date_ingestion"] = pd.to_datetime(
        df["date_ingestion"]
    )

    df["heure"] = (
        df["date_ingestion"]
        .dt.hour
    )

    df["jour_semaine"] = (
        df["date_ingestion"]
        .dt.dayofweek
    )

    df["est_weekend"] = (
        df["jour_semaine"]
        .apply(
            lambda x: 1 if x >= 5 else 0
        )
    )

    # Même méthode d'encodage que celle utilisée
    # dans le dashboard Streamlit.
    df["station_id_encoded"] = (
        df["id"]
        .astype("category")
        .cat.codes
    )

    return df


# ============================================================
# BENCHMARK ET ENTRAINEMENT
# ============================================================

def comparer_et_selectionner_modele(df):
    """
    Compare plusieurs algorithmes de régression.

    Le meilleur modèle est identifié selon son score R².

    En parallèle, un Random Forest dédié est toujours sauvegardé
    sous le nom random_forest_velops.pkl afin d'être utilisé
    de manière stable par l'application Streamlit.
    """

    print(
        "=== [MLOPS] Début du benchmark des modèles ==="
    )

    features = [
        "heure",
        "jour_semaine",
        "est_weekend",
        "station_id_encoded",
        "places_libres",
    ]

    target = "velos_dispo"

    # Nettoyage des valeurs manquantes
    df_clean = df.dropna(
        subset=features + [target]
    )

    if len(df_clean) < 10:
        raise ValueError(
            "Pas assez de données pour entraîner les modèles."
        )

    X = df_clean[features]
    y = df_clean[target]

    # Même séparation pour tous les modèles
    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.20,
            random_state=42,
        )
    )

    print(
        f"Nombre total d'observations : {len(df_clean)}"
    )

    print(
        f"Données d'entraînement : {len(X_train)}"
    )

    print(
        f"Données de test : {len(X_test)}"
    )

    # ========================================================
    # MODELES A COMPARER
    # ========================================================

    modeles = {
        "Régression Linéaire": LinearRegression(),

        "Ridge (Régularisé)": Ridge(
            alpha=1.0
        ),

        "Arbre de Décision": DecisionTreeRegressor(
            max_depth=10,
            random_state=42,
        ),

        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=12,
            random_state=42,
        ),

        "Gradient Boosting": GradientBoostingRegressor(
            random_state=42
        ),
    }

    resultats = []

    meilleur_score_r2 = -float("inf")
    meilleur_nom = ""
    meilleur_modele = None

    # ========================================================
    # BENCHMARK
    # ========================================================

    for nom, modele in modeles.items():

        modele.fit(
            X_train,
            y_train,
        )

        y_pred = modele.predict(
            X_test
        )

        mae = mean_absolute_error(
            y_test,
            y_pred,
        )

        r2 = r2_score(
            y_test,
            y_pred,
        )

        resultats.append(
            {
                "Modèle": nom,
                "MAE (Erreur en vélos)": mae,
                "Score R²": r2,
            }
        )

        if r2 > meilleur_score_r2:
            meilleur_score_r2 = r2
            meilleur_nom = nom
            meilleur_modele = modele

    # ========================================================
    # RESULTATS DU BENCHMARK
    # ========================================================

    df_resultats = pd.DataFrame(
        resultats
    )

    print(
        "\n--- TABLEAU COMPARATIF DES PERFORMANCES ---"
    )

    print(
        df_resultats.to_string(
            index=False
        )
    )

    print(
        f"\n[SÉLECTION] Meilleur modèle : "
        f"{meilleur_nom} "
        f"(R² = {meilleur_score_r2:.3f})"
    )

    # ========================================================
    # MODELE DEDIE AU DASHBOARD STREAMLIT
    # ========================================================

    modele_streamlit = RandomForestRegressor(
        n_estimators=100,
        max_depth=12,
        random_state=42,
    )

    modele_streamlit.fit(
        X_train,
        y_train,
    )

    prediction_streamlit = (
        modele_streamlit.predict(
            X_test
        )
    )

    mae_streamlit = mean_absolute_error(
        y_test,
        prediction_streamlit,
    )

    r2_streamlit = r2_score(
        y_test,
        prediction_streamlit,
    )

    print(
        "\n--- MODELE STREAMLIT ---"
    )

    print(
        f"Algorithme : Random Forest"
    )

    print(
        f"MAE : {mae_streamlit:.3f}"
    )

    print(
        f"R²  : {r2_streamlit:.3f}"
    )

    # ========================================================
    # DOSSIER DES MODELES
    # ========================================================

    models_dir = os.path.join(
        os.path.dirname(__file__),
        "models",
    )

    os.makedirs(
        models_dir,
        exist_ok=True,
    )

    # ========================================================
    # SAUVEGARDE DU MEILLEUR MODELE
    # ========================================================

    nom_fichier_modele = (
        meilleur_nom
        .lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("é", "e")
        .replace("è", "e")
        .replace("à", "a")
        + "_velops.pkl"
    )

    best_model_path = os.path.join(
        models_dir,
        nom_fichier_modele,
    )

    joblib.dump(
        meilleur_modele,
        best_model_path,
    )

    print(
        f"\n[MLOPS] Meilleur modèle sauvegardé : "
        f"{best_model_path}"
    )

    # ========================================================
    # SAUVEGARDE DU MODELE STREAMLIT
    # ========================================================

    streamlit_model_path = os.path.join(
        models_dir,
        "random_forest_velops.pkl",
    )

    joblib.dump(
        modele_streamlit,
        streamlit_model_path,
    )

    print(
        f"[MLOPS] Modèle Streamlit sauvegardé : "
        f"{streamlit_model_path}"
    )

    print(
        "\n=== [MLOPS] Fin de l'entraînement ==="
    )

    return meilleur_modele


# ============================================================
# PROGRAMME PRINCIPAL
# ============================================================

if __name__ == "__main__":

    df_brut = (
        charger_donnees_historiques()
    )

    if not df_brut.empty:

        df_processed = (
            feature_engineering(
                df_brut
            )
        )

        comparer_et_selectionner_modele(
            df_processed
        )

    else:

        print(
            "[ML] Erreur : données insuffisantes."
        )
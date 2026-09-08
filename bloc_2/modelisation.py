import os
import sqlite3
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

def charger_donnees_historiques():
    """Extrait l'historique des stations depuis la base SQLite parente."""
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "velops_paris.db"))
    if not os.path.exists(db_path):
        print(f"[ERREUR] Base de données introuvable : {db_path}")
        return pd.DataFrame()
    
    conn = sqlite3.connect(db_path)
    query = """
        SELECT s.id, s.nom, s.velos_dispo, s.places_libres, 
               a.nom as arrondissement, s.date_ingestion
        FROM stations s
        INNER JOIN arrondissements a ON s.id_arrondissement = a.id_arrondissement
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def feature_engineering(df):
    """Prépare les features temporelles et catégorielles."""
    df['date_ingestion'] = pd.to_datetime(df['date_ingestion'])
    df['heure'] = df['date_ingestion'].dt.hour
    df['jour_semaine'] = df['date_ingestion'].dt.dayofweek
    df['est_weekend'] = df['jour_semaine'].apply(lambda x: 1 if x >= 5 else 0)
    df['station_id_encoded'] = df['id'].astype('category').cat.codes
    return df

def comparer_et_selectionner_modele(df):
    """Teste plusieurs modèles, compare leurs performances et sélectionne le meilleur de manière dynamique."""
    print("=== [MLOPS] Début du benchmark des modèles ===")
    
    features = ['heure', 'jour_semaine', 'est_weekend', 'station_id_encoded', 'places_libres']
    target = 'velos_dispo'
    
    df_clean = df.dropna(subset=features + [target])
    X = df_clean[features]
    y = df_clean[target]
    
    # Même découpage pour tous les modèles pour un test équitable
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Dictionnaire des modèles à tester (avec des contraintes de régularisation pour éviter l'overfitting)
    modeles = {
        "Régression Linéaire": LinearRegression(),
        "Ridge (Régularisé)": Ridge(alpha=1.0),
        "Arbre de Décision": DecisionTreeRegressor(max_depth=10, random_state=42),
        "Random Forest": RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(random_state=42)
    }
    
    resultats = []
    meilleur_score_r2 = -float('inf')
    meilleur_nom = ""
    meilleur_modele = None
    
    for nom, modele in modeles.items():
        # Entraînement
        modele.fit(X_train, y_train)
        # Prédiction
        y_pred = modele.predict(X_test)
        
        # Calcul des métriques
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        resultats.append({"Modèle": nom, "MAE (Erreur en vélos)": mae, "Score R²": r2})
        
        # Sélection dynamique du meilleur basé sur le R²
        if r2 > meilleur_score_r2:
            meilleur_score_r2 = r2
            meilleur_nom = nom
            meilleur_modele = modele

    # Affichage sous forme de tableau comparatif propre
    df_resultats = pd.DataFrame(resultats)
    print("\n--- TABLEAU COMPARATIF DES PERFORMANCES ---")
    print(df_resultats.to_string(index=False))
    
    print(f"\n🏆 [SÉLECTION] Le meilleur modèle est : **{meilleur_nom}** (R² = {meilleur_score_r2:.2f})")
    
    # Sauvegarde dynamique du meilleur modèle avec son nom sémantique adapté
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    
    nom_fichier_modele = (
        meilleur_nom.lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("é", "e")
        .replace("à", "a") 
        + "_velops.pkl"
    )
    model_path = os.path.join(models_dir, nom_fichier_modele)
    
    joblib.dump(meilleur_modele, model_path)
    print(f"[MLOPS] Le modèle gagnant ({meilleur_nom}) a été sauvegardé avec succès dans : {model_path}")
    
    return meilleur_modele

if __name__ == "__main__":
    df_brut = charger_donnees_historiques()
    if not df_brut.empty:
        df_processed = feature_engineering(df_brut)
        comparer_et_selectionner_modele(df_processed)
    else:
        print("[ML] Erreur : Données insuffisantes.")
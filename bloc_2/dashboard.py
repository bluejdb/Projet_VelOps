import os
import sqlite3
import pandas as pd
import streamlit as st
import joblib

# Configuration de la page Streamlit
st.set_page_config(
    page_title="VelOps Paris - Dashboard MLOps",
    page_icon="🚲",
    layout="wide"
)

# Fonction pour charger les données depuis SQLite
@st.cache_data
def charger_donnees():
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "velops_paris.db"))
    if not os.path.exists(db_path):
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

# Fonction pour charger le modèle entraîné
@st.cache_resource
def charger_modele():
    model_path = os.path.join(os.path.dirname(__file__), "models", "random_forest_velops.pkl")
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

df_stations = charger_donnees()
modele_ml = charger_modele()

# En-tête du Dashboard
st.title("🚲 VelOps Paris : Supervision et Prédiction des Flux")
st.markdown("Tableau de bord MLOps de restitution des disponibilités de vélos en libre-service.")

if df_stations.empty:
    st.error("⚠️ Aucune donnée disponible dans la base SQLite. Veuillez exécuter le pipeline de collecte.")
else:
    # 1. KPIs globaux en haut de page
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Stations Surveillées", len(df_stations))
    with col2:
        st.metric("Moyenne Vélos Disponibles", f"{df_stations['velos_dispo'].mean():.1f}")
    with col3:
        st.metric("Moyenne Places Libres", f"{df_stations['places_libres'].mean():.1f}")

    st.markdown("---")

    # 2. Section de Simulation Prédictive (MLOps en action)
    st.header("🎯 Simulateur de Prédiction de Disponibilité (Modèle Random Forest)")
    
    if modele_ml is None:
        st.warning("⚠️ Aucun modèle entraîné trouvé dans `models/`. Veuillez lancer `modelisation.py`.")
    else:
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            station_selectionnee = st.selectbox("Sélectionner une station", df_stations['nom'].unique())
        with col_s2:
            heure_choisie = st.slider("Heure de la journée", 0, 23, 8)
        with col_s3:
            jour_choisi = st.selectbox("Jour de la semaine", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"])
            
        # Conversion du jour en format numérique (0-6)
        jours_map = {"Lundi": 0, "Mardi": 1, "Mercredi": 2, "Jeudi": 3, "Vendredi": 4, "Samedi": 5, "Dimanche": 6}
        jour_num = jours_map[jour_choisi]
        est_weekend = 1 if jour_num >= 5 else 0
        
        # Récupération de la station pour trouver ses caractéristiques par défaut
        st_data = df_stations[df_stations['nom'] == station_selectionnee].iloc[0]
        station_categories = df_stations['id'].astype('category')

        station_code_map = dict(
           zip(
               df_stations['id'],
               station_categories.cat.codes
          )
        )

        station_id_encoded = station_code_map[st_data['id']]
        places_libres_actuelles = st_data['places_libres']
        
        # Bouton de prédiction
        if st.button("Lancer la prédiction"):
            # Features attendues : ['heure', 'jour_semaine', 'est_weekend', 'station_id_encoded', 'places_libres']
            X_input = pd.DataFrame([[heure_choisie, jour_num, est_weekend, station_id_encoded, places_libres_actuelles]], 
                                   columns=['heure', 'jour_semaine', 'est_weekend', 'station_id_encoded', 'places_libres'])
            
            prediction = modele_ml.predict(X_input)[0]
            st.success(f"✨ **Prédiction de vélos disponibles :** {max(0, int(round(prediction)))} vélos (pour la station {station_selectionnee})")

    st.markdown("---")

    # 3. Visualisation Tabulaire des données brutes
    st.header("📊 Aperçu des Données en Base")
    st.dataframe(df_stations[['nom', 'arrondissement', 'velos_dispo', 'places_libres', 'date_ingestion']], use_container_width=True)
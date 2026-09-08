import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration du style des graphiques
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)

def charger_et_preparer_donnees():
    print("=== [EDA] Connexion à la base de données VelOps ===")
    conn = sqlite3.connect("../velops_paris.db")
    
    # Requête de jointure entre stations et arrondissements
    query = """
        SELECT 
            s.id AS station_id,
            s.nom AS station_nom,
            s.velos_dispo,
            s.places_libres,
            a.nom AS arrondissement,
            s.date_ingestion
        FROM stations s
        INNER JOIN arrondissements a ON s.id_arrondissement = a.id_arrondissement
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Nettoyage et typage
    df['date_ingestion'] = pd.to_datetime(df['date_ingestion'])
    df['velos_dispo'] = pd.to_numeric(df['velos_dispo'], errors='coerce').fillna(0).astype(int)
    df['places_libres'] = pd.to_numeric(df['places_libres'], errors='coerce').fillna(0).astype(int)
    
    print(f"[EDA] Données chargées avec succès : {df.shape[0]} lignes, {df.shape[1]} colonnes.")
    return df

def generer_statistiques_descriptives(df):
    print("\n=== [STATISTIQUES DESCRIPTIVES] ===")
    stats = df[['velos_dispo', 'places_libres']].describe()
    print(stats)
    return stats

def tracer_top_stations(df):
    print("\n=== [VISUALISATION] Top 10 des stations par disponibilité moyenne ===")
    
    # 1. On regroupe par nom de station et on fait la moyenne (ou .max() selon votre besoin)
    df_grouped = df.groupby('station_nom')['velos_dispo'].mean().reset_index()
    
    # 2. On trie pour garder les 10 stations avec la plus forte disponibilité moyenne
    top_stations = df_grouped.sort_values(by='velos_dispo', ascending=False).head(10)
    
    plt.figure(figsize=(10, 6))
    # Correction du warning Seaborn en ajoutant hue et legend=False
    sns.barplot(x='velos_dispo', y='station_nom', data=top_stations, hue='station_nom', palette='Blues_r', legend=False)
    
    plt.title('Top 10 des Stations - Disponibilité Moyenne des Vélos', fontsize=14, fontweight='bold')
    plt.xlabel('Nombre moyen de vélos disponibles', fontsize=12)
    plt.ylabel('Nom de la station', fontsize=12)
    plt.tight_layout()
    plt.savefig('top_stations_velos.png', dpi=300)
    plt.close()
    print("[VISUALISATION] Graphique 'top_stations_velos.png' mis à jour et sauvegardé.")

def tracer_correlation(df):
    print("\n=== [VISUALISATION] Matrice de corrélation ===")
    correlation = df[['velos_dispo', 'places_libres']].corr()
    
    plt.figure()
    sns.heatmap(correlation, annot=True, cmap='coolwarm', vmin=-1, vmax=1, fmt='.2f')
    plt.title('Corrélation : Vélos Disponibles vs Places Libres', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('correlation_velos_places.png', dpi=300)
    plt.close()
    print("[VISUALISATION] Graphique 'correlation_velos_places.png' sauvegardé.")

if __name__ == "__main__":
    df_velops = charger_et_preparer_donnees()
    generer_statistiques_descriptives(df_velops)
    tracer_top_stations(df_velops)
    tracer_correlation(df_velops)
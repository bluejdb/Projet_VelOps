import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import sqlite3
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# --- CORRECTION CHEMIN .ENV ---
PROJECT_ROOT = Path(__file__).resolve().parents[2]
env_path = PROJECT_ROOT / ".env"
DB_PATH = PROJECT_ROOT / "velops_paris.db"

load_dotenv(dotenv_path=env_path)

# ==============================================================================
# 1. API EXTERNE SÉCURISÉE (C1.4.1)
# ==============================================================================
def recuperer_donnees_api():
    print("=== [API] Début de la collecte via l'API Open Data Paris ===")
    
    url_api = os.getenv("PARIS_API_URL")
    
    if not url_api:
        print(f"[SÉCURITÉ] Erreur : L'URL de l'API est introuvable ! (Chemin cherché : {env_path})")
        return []
        
    try:
        reponse = requests.get(url_api)
        print(f"[API] Code de statut HTTP reçu : {reponse.status_code}")
        
        if reponse.status_code == 200:
            results = reponse.json().get('results', [])
            print(f"[API] Connexion réussie ! {len(results)} stations récupérées.")
            return results
        else:
            print(f"[API] Erreur du serveur : Statut {reponse.status_code}")
            return []
            
    except Exception as e:
        print(f"[API] Erreur technique critique : {e}")
        return []

# ==============================================================================
# 2. WEB CRAWLING & WEB SCRAPING (WIKIPÉDIA)
# ==============================================================================
def crawler_et_scraper_paris():
    print("\n=== [SCRAPING & CRAWLING] Exploration de Wikipédia ===")
    liens_arrondissements = [
        f"https://fr.wikipedia.org/wiki/{i}er_arrondissement_de_Paris" if i == 1 else f"https://fr.wikipedia.org/wiki/{i}e_arrondissement_de_Paris"
        for i in range(1, 21)
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    donnees_scrapees = []

    for idx, url in enumerate(liens_arrondissements[:3], start=1):
        try:
            rep = requests.get(url, headers=headers)
            soup = BeautifulSoup(rep.text, 'html.parser')
            titre = soup.find('h1', {'id': 'firstHeading'}).text.strip()
            
            paragraphes = soup.find_all('p')
            texte_intro = "Paris"
            for p in paragraphes:
                if len(p.text.strip()) > 20:
                    texte_intro = p.text.strip()[:50] + "..."
                    break
            
            donnees_scrapees.append((idx, titre, texte_intro))
            print(f"[SCRAPING] Données récupérées pour l'arrondissement : {idx}")
        except Exception as e:
            print(f"[SCRAPING] Erreur idx {idx}: {e}")
            
    return donnees_scrapees

# ==============================================================================
# 3. NETTOYAGE ET TRANSFORMATION
# ==============================================================================
def nettoyer_et_transformer_donnees(stations_brutes, arrondissements_bruts):
    print("\n=== [TRANSFORMATION] Phase de nettoyage et de formatage des données ===")
    timestamp_ingestion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[C1.3.1] Horodatage appliqué à ce lot de données : {timestamp_ingestion}")
    
    stations_nettoyees = []
    arrondissements_nettoyes = []
    
    for idx, st in enumerate(stations_brutes):
        id_station = str(st.get('stationcode', f"ST-{idx}")).strip()
        nom_station = str(st.get('name', 'Nom Inconnu')).strip().upper()
        
        try:
            velos_dispo = int(st.get('numbikesavailable', 0))
        except (ValueError, TypeError):
            velos_dispo = 0
            
        try:
            places_libres = int(st.get('numdocksavailable', 0))
        except (ValueError, TypeError):
            places_libres = 0
            
        arr_simule = (idx % 3) + 1 
        stations_nettoyees.append((id_station, nom_station, velos_dispo, places_libres, arr_simule, timestamp_ingestion))

    for arr in arrondissements_bruts:
        id_arr = int(arr[0])
        nom_arr = str(arr[1]).replace(" arrondissement de Paris", "").strip()
        desc_arr = str(arr[2]).strip()
        
        arrondissements_nettoyes.append((id_arr, nom_arr, desc_arr, timestamp_ingestion))
        
    print(f"[C1.3.2] Nettoyage terminé. {len(stations_nettoyees)} stations et {len(arrondissements_nettoyes)} arrondissements traités.")
    return stations_nettoyees, arrondissements_nettoyes

# ==============================================================================
# 4. STOCKAGE HISTORIQUE ET REQUÊTES SQL
# ==============================================================================
def stocker_et_valider_sql(stations_clean, arrondissements_clean):
    print("\n=== [SQL] Connexion à la base de données SQLite (Mode Historique) ===")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Rafraîchissement des dimensions de référence
    cursor.execute("DROP TABLE IF EXISTS arrondissements")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS arrondissements (
            id_arrondissement INTEGER PRIMARY KEY,
            nom TEXT,
            description TEXT,
            date_ingestion TEXT
        )
    """)
    
    # Création de la table historique si elle n'existe pas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stations (
            id_enregistrement INTEGER PRIMARY KEY AUTOINCREMENT,
            id TEXT,
            nom TEXT,
            velos_dispo INTEGER,
            places_libres INTEGER,
            id_arrondissement INTEGER,
            date_ingestion TEXT
        )
    """)
    
    for arr in arrondissements_clean:
        cursor.execute("INSERT INTO arrondissements VALUES (?, ?, ?, ?)", arr)
        
    # Insertion en mode Append-Only (cumul de l'historique)
    for st in stations_clean:
        cursor.execute("""
            INSERT INTO stations (id, nom, velos_dispo, places_libres, id_arrondissement, date_ingestion) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, st)
        
    conn.commit()
    print("[SQL] Nouveau lot de données inséré dans l'historique avec succès.")
    
    print("\n=== [SQL] Aperçu des derniers enregistrements de l'historique ===")
    query = """
        SELECT stations.nom, stations.velos_dispo, arrondissements.nom, stations.date_ingestion
        FROM stations
        INNER JOIN arrondissements ON stations.id_arrondissement = arrondissements.id_arrondissement
        ORDER BY stations.id_enregistrement DESC
        LIMIT 3
    """
    cursor.execute(query)
    resultats = cursor.fetchall()
    
    for l in resultats:
        print(f"Station : {l[0]} | Vélos : {l[1]} | Zone : {l[2]} | Collecté le : {l[3]}")
        
    conn.close()
    print("\n=== Fin du Pipeline Sécurisé avec succès ===")

if __name__ == "__main__":
    brutes_api = recuperer_donnees_api()
    brutes_scrap = crawler_et_scraper_paris()
    clean_api, clean_scrap = nettoyer_et_transformer_donnees(brutes_api, brutes_scrap)
    stocker_et_valider_sql(clean_api, clean_scrap)
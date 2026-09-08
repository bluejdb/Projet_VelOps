# VelOps Paris

## Présentation du projet

**VelOps Paris** est un projet de Data Engineering visant à collecter, transformer, historiser et exploiter les données de disponibilité des stations Vélib’ à Paris.

Le projet a été développé dans le cadre d’un cursus **Master Data Engineer – RNCP Niveau 7**.

L’objectif métier est de construire progressivement une infrastructure Data capable de :

* collecter les données de disponibilité des stations Vélib’ ;
* historiser les observations ;
* nettoyer et transformer les données ;
* entraîner un modèle de Machine Learning ;
* exposer les résultats via des services Data ;
* orchestrer les traitements ;
* industrialiser les déploiements ;
* superviser les pipelines et les composants de l’infrastructure.

---

## État actuel du projet

La première chaîne de traitement fonctionnelle repose actuellement sur l’architecture suivante :

```text
Open Data Paris
      |
      v
Python - Ingestion
      |
      v
Nettoyage / Transformation
      |
      v
SQLite - Historisation
      |
      v
Random Forest - Machine Learning
```

### Fonctionnalités opérationnelles

Le projet permet actuellement :

* la récupération des données depuis l’API Open Data Paris ;
* la collecte complémentaire de données par scraping ;
* le nettoyage et le formatage des observations ;
* l’ajout d’un horodatage d’ingestion ;
* l’historisation des données dans SQLite ;
* l’entraînement d’un modèle Random Forest ;
* l’évaluation du modèle avec les métriques MAE, RMSE et R² ;
* la sauvegarde locale du modèle entraîné.

---

## Architecture cible - Bloc 4

Le Bloc 4 vise à faire évoluer cette première architecture vers une infrastructure Data plus industrialisée.

Architecture cible :

```text
          Sources de données
     API Vélib' / Sources externes
                 |
                 v
         Ingestion Python
                 |
                 v
        API / Temps réel
                 |
                 v
          Zone Bronze
        Données brutes
                 |
                 v
       Traitements Spark
                 |
                 v
          Zone Silver
       Données nettoyées
                 |
                 v
          SQL / dbt
                 |
                 v
           Zone Gold
       Données métier
                 |
        +--------+--------+
        |                 |
        v                 v
 Machine Learning     Data Visualisation
```

L’industrialisation prévoit également :

```text
Airflow
   |
   +--> Orchestration des pipelines

GitHub Actions
   |
   +--> CI/CD

Docker
   |
   +--> Conteneurisation

Prometheus / Grafana
   |
   +--> Monitoring et supervision
```

---

## Structure du dépôt

```text
Projet_VelOps/
|
+-- src/
|   +-- ingestion/
|   |   +-- pipeline.py
|   |
|   +-- prediction/
|       +-- train_model.py
|
+-- airflow/
|
+-- spark/
|
+-- dbt/
|
+-- sql/
|
+-- monitoring/
|
+-- tests/
|
+-- docs/
|
+-- models/
|
+-- bloc_2/
|
+-- bloc_3/
|
+-- requirements.txt
+-- run_pipeline.bat
+-- .gitignore
+-- README.md
```

Les répertoires `airflow`, `spark`, `dbt`, `sql`, `monitoring`, `tests` et `docs` sont destinés aux composants du Bloc 4 qui seront progressivement implémentés.

---

## Technologies

### Technologies actuellement utilisées

* Python
* Requests
* BeautifulSoup
* Pandas
* SQLite
* scikit-learn
* Random Forest
* Git

### Technologies prévues pour l’industrialisation

* FastAPI
* Redis
* Apache Airflow
* Apache Spark
* dbt
* Docker
* GitHub Actions
* Pytest
* Prometheus
* Grafana

Une architecture Cloud utilisant notamment AWS S3, EMR, MWAA et Snowflake est également étudiée dans le cadre de la conception de l’infrastructure cible.

---

## Installation

### 1. Cloner le dépôt

```bash
git clone <URL_DU_DEPOT>
cd Projet_VelOps
```

### 2. Créer un environnement virtuel

Sous Windows :

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Installer les dépendances

```powershell
pip install -r requirements.txt
```

---

## Configuration

Le projet utilise un fichier `.env` pour stocker les paramètres de configuration.

Exemple :

```env
PARIS_API_URL=<URL_API>
```

Le fichier `.env` n’est pas versionné dans Git.

Cette exclusion permet d’éviter l’exposition de paramètres sensibles ou spécifiques à l’environnement d’exécution.

---

## Exécution du pipeline d’ingestion

Depuis la racine du projet :

```powershell
python .\src\ingestion\pipeline.py
```

Le pipeline effectue les traitements suivants :

```text
1. Connexion à l’API
2. Récupération des stations
3. Scraping complémentaire
4. Nettoyage des données
5. Horodatage
6. Chargement dans SQLite
7. Historisation
```

---

## Entraînement du modèle

Depuis la racine :

```powershell
python .\src\prediction\train_model.py
```

Le script :

* charge les observations depuis SQLite ;
* prépare les variables explicatives ;
* sépare les données en jeux d’entraînement et de test ;
* entraîne un Random Forest ;
* calcule les métriques d’évaluation ;
* sauvegarde le modèle.

Exemple de métriques obtenues sur la version actuelle :

```text
MAE  : environ 6.2
RMSE : environ 8.8
R²   : environ 0.39
```

Ces résultats correspondent à un prototype et ne représentent pas encore une performance de production.

---

## Limites actuelles

La version actuelle du projet est une première implémentation fonctionnelle.

Plusieurs éléments sont encore en cours d’industrialisation :

* l’orchestration des traitements ;
* le traitement distribué ;
* la modélisation analytique Silver / Gold ;
* les tests automatisés ;
* la CI/CD ;
* l’exposition des données via API ;
* la supervision ;
* la conteneurisation ;
* la gestion des incidents et du maintien en condition opérationnelle.

Certaines données géographiques utilisées dans le prototype doivent également être enrichies avant une utilisation en production.

---

## Objectifs du Bloc 4

Le Bloc 4 couvre notamment les compétences suivantes :

### Analyse et cadrage

* identification des besoins métier ;
* étude de la volumétrie ;
* identification des contraintes ;
* sélection des technologies ;
* estimation des coûts.

### Architecture Data

* conception d’une architecture Data ;
* organisation Bronze / Silver / Gold ;
* modélisation analytique ;
* gestion des droits d’accès.

### Pipelines

Mise en œuvre de plusieurs modes de traitement :

* traitement Python / temps réel ;
* orchestration avec Airflow ;
* calcul distribué avec Spark ;
* transformations SQL / dbt.

### Industrialisation

* Git ;
* Docker ;
* tests automatisés ;
* CI/CD avec GitHub Actions.

### Supervision

* collecte de métriques ;
* supervision des pipelines ;
* visualisation ;
* alertes.

### Exploitation

* documentation technique ;
* maintenance ;
* procédures de tests ;
* gestion des incidents ;
* maintien en condition opérationnelle.

---

## Sécurité et bonnes pratiques

Les fichiers suivants ne sont pas versionnés :

```text
.env
.venv/
*.db
*.sqlite
*.pkl
*.joblib
```

Cela permet de ne pas publier :

* les secrets et variables d’environnement ;
* les bases de données locales ;
* les environnements virtuels ;
* les artefacts Machine Learning générés localement.

---

## Auteur

**Blue Jdb**

Master Data Engineer
Projet VelOps Paris
2026


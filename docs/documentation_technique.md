# VelOps Paris - Documentation Technique



## 1. Présentation générale



VelOps Paris est un prototype de plateforme Data permettant de collecter, transformer, exposer et superviser des données relatives à la disponibilité des stations Vélib'.



L'objectif principal est de démontrer une architecture Data industrialisable répondant aux exigences du Bloc 4.



Le prototype local implémente :



- ingestion Python ;

- stockage SQLite ;

- modèle analytique en étoile ;

- transformations dbt ;

- traitement distribué Spark ;

- orchestration Airflow ;

- API FastAPI ;

- conteneurisation Docker ;

- tests automatisés pytest ;

- CI/CD GitHub Actions ;

- supervision Prometheus ;

- visualisation Grafana ;

- règles d'alerte Prometheus.



Les composants Cloud AWS et Snowflake appartiennent à l'architecture cible et ne sont pas déployés dans le prototype local.



## 2. Architecture générale



Flux principal :



`API Open Data Paris -> Python -> SQLite -> Modèle en étoile -> API / Spark / dbt`



Industrialisation :



`GitHub -> GitHub Actions -> Tests -> Build Docker`



Orchestration :



`Airflow -> Ingestion -> Chargement étoile -> Spark`



Supervision :



`FastAPI -> /metrics -> Prometheus -> Grafana`



## 3. Structure du projet



Principaux répertoires :



- `src/ingestion` : collecte et préparation des données ;

- `src/transformation` : chargement du modèle analytique ;

- `src/prediction` : entraînement du modèle ML ;

- `src/api` : API FastAPI ;

- `sql` : définition du schéma SQL ;

- `spark` : traitements distribués PySpark ;

- `airflow` : orchestration ;

- `dbt` : transformations analytiques ;

- `tests` : tests automatisés ;

- `monitoring` : Prometheus, Grafana et alertes ;

- `docs` : documentation d'exploitation et de recette.



## 4. Ingestion des données



Le script principal est :



`src/ingestion/pipeline.py`



Les données sont récupérées depuis l'API Open Data Paris.



Le pipeline réalise :



1. appel HTTP ;

2. récupération des stations ;

3. enrichissement avec des informations d'arrondissements ;

4. nettoyage ;

5. ajout d'un horodatage ;

6. insertion dans SQLite.



Base source :



`velops\_paris.db`



## 5. Modèle analytique



Le schéma analytique est défini dans :



`sql/schema.sql`



Le modèle utilisé est un schéma en étoile.



Tables principales :



- `dim\_station`

- `dim\_arrondissement`

- `dim\_temps`

- `fait\_disponibilite`



Le script de chargement est :



`src/transformation/load\_star\_schema.py`



Base analytique :



`velops\_star.db`



## 6. Transformations dbt



Le projet dbt est situé dans :



`dbt/`



Le staging est matérialisé sous forme de vue.



Le mart analytique est matérialisé sous forme de table.



Principaux modèles :



- `stg\_disponibilite`

- `mart\_disponibilite\_arrondissement`



Les tests dbt vérifient notamment :



- valeurs non nulles ;

- unicité de certaines clés.



Résultat de validation :



`8 tests PASS`



## 7. Traitement Spark



Le traitement distribué est défini dans :



`spark/transform\_velops.py`



Le script :



1. charge les données SQLite ;

2. crée un DataFrame Spark ;

3. filtre les valeurs invalides ;

4. déduplique les observations ;

5. calcule des agrégations par arrondissement ;

6. exporte les résultats.



Le traitement est compatible avec :



- Windows local ;

- environnement Linux Docker.



La portabilité est assurée via :



`sys.executable`



## 8. Orchestration Airflow



Le DAG principal est :



`velops\_pipeline`



Le fichier est situé dans :



`airflow/dags/velops\_pipeline.py`



Le DAG est planifié à :



`02:00 chaque jour`



Chaîne des tâches :



`ingestion\_velib -> load\_star\_schema -> spark\_transformation`



Un run complet a été validé avec succès.



## 9. API FastAPI



L'API est définie dans :



`src/api/main.py`



Principaux endpoints :



- `/`

- `/health`

- `/stations`

- `/stations/{station\_id}`

- `/predict/{station\_id}`

- `/metrics`



L'API expose les données du modèle analytique et permet également l'accès à la prédiction ML.



## 10. Modèle de prédiction



Le modèle est entraîné dans :



`src/prediction/train\_model.py`



Algorithme :



`RandomForestRegressor`



Variables utilisées :



- `places\_libres`

- `id\_arrondissement`



Variable cible :



`velos\_dispo`



Le modèle est sérialisé dans :



`models/random\_forest\_model.pkl`



Ce fichier n'est pas versionné dans Git.



## 11. Docker



Le fichier principal est :



`Dockerfile`



L'image construite localement est :



`velops-api:1.0`



Le conteneur expose le port :



`8000`



Un test de santé Docker a été validé sur :



`/health`



## 12. Tests automatisés



Les tests Python sont situés dans :



`tests/`



Ils couvrent notamment :



- disponibilité de l'API ;

- endpoint de santé ;

- consultation des stations ;

- gestion des stations inexistantes ;

- présence de la base analytique ;

- intégrité des clés étrangères ;

- présence des faits ;

- alimentation des dimensions.



Résultat :



`9 tests PASS`



## 13. CI/CD GitHub Actions



Le workflow est situé dans :



`.github/workflows/ci.yml`



Il s'exécute sur :



- push sur `main` ;

- pull request vers `main`.



Étapes principales :



1. checkout du dépôt ;

2. installation de Python ;

3. installation des dépendances ;

4. compilation Python ;

5. création de données de test ;

6. construction du modèle en étoile ;

7. entraînement ML ;

8. exécution de pytest ;

9. construction Docker.



Le workflow a été validé avec le statut :



`Success`



## 14. Supervision Prometheus



Les métriques sont exposées via :



`/metrics`



Prometheus collecte les métriques toutes les 5 secondes.



Principales métriques :



- `velops\_api\_requests\_total`

- `velops\_api\_request\_duration\_seconds`

- `up`



Le fichier de configuration est :



`monitoring/prometheus.yml`



## 15. Dashboard Grafana



Le dashboard principal est :



`VelOps - Supervision API`



Le fichier JSON versionné est :



`monitoring/velops\_grafana\_dashboard.json`



Indicateurs présents :



- état de l'API ;

- débit ;

- latence P99 ;

- taux d'erreurs 5xx ;

- débit par endpoint ;

- latence P50 / P95 / P99 ;

- codes HTTP ;

- volume cumulé de requêtes.



## 16. Alerting



Les règles sont définies dans :



`monitoring/alerts.yml`



Règles principales :



- `VelOpsAPIDown`

- `VelOpsHighLatency`

- `VelOpsHighErrorRate`



Seuils :



- API indisponible pendant 30 secondes ;

- latence P99 supérieure à 100 ms pendant 1 minute ;

- taux d'erreurs 5xx supérieur à 5 % pendant 1 minute.



## 17. Sécurité



Mesures appliquées :



- `.env` ignoré par Git ;

- bases SQLite ignorées ;

- modèles ML ignorés ;

- caches et logs ignorés ;

- tests automatisés avant intégration ;

- séparation entre configuration locale et architecture cible.



Les secrets de production devront être externalisés dans un gestionnaire de secrets.



## 18. Architecture cible Cloud



L'architecture cible prévoit :



- AWS S3 pour la couche Bronze ;

- AWS EMR pour Spark ;

- AWS MWAA pour Airflow ;

- Snowflake pour Silver et Gold ;

- dbt pour les transformations ;

- Terraform pour l'infrastructure ;

- Prometheus / Grafana pour la supervision ;

- gestion centralisée des secrets.



Cette architecture cible n'est pas entièrement déployée dans le prototype local.



## 19. Limites actuelles



Les limites du prototype sont :



- stockage SQLite local ;

- nombre limité d'arrondissements enrichis ;

- infrastructure non hautement disponible ;

- absence de gestionnaire de secrets ;

- absence de déploiement Cloud réel ;

- modèle ML de démonstration ;

- volumétrie limitée par rapport à une production réelle.



## 20. Conclusion



Le prototype VelOps démontre une chaîne Data complète allant de la collecte jusqu'à la supervision.



Les principaux objectifs du Bloc 4 sont couverts par une implémentation locale reproductible, testée, conteneurisée, orchestrée, supervisée et versionnée.



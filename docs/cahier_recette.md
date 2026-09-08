# VelOps Paris - Cahier de Recette



## 1. Objectif



Le cahier de recette permet de vérifier que l'infrastructure VelOps répond aux exigences fonctionnelles, structurelles et de sécurité définies pour le prototype.



Chaque test précise :



- l'objectif ;

- le prérequis ;

- l'action réalisée ;

- le résultat attendu ;

- le statut.



## 2. Tests fonctionnels



### RF-01 - Vérification de l'API racine



Objectif :



Vérifier que l'API FastAPI est disponible.



Action :



Appeler l'endpoint :



`GET /`



Résultat attendu :



- code HTTP 200 ;

- statut applicatif `running`.



Statut :



`Validé`



### RF-02 - Vérification de l'état de santé



Objectif :



Vérifier que l'API et la base analytique sont accessibles.



Action :



Appeler :



`GET /health`



Résultat attendu :



- code HTTP 200 ;

- `status = ok` ;

- `database = ok`.



Statut :



`Validé`



### RF-03 - Consultation des stations



Objectif :



Vérifier la consultation de la dimension station.



Action :



Appeler :



`GET /stations?limit=5`



Résultat attendu :



- code HTTP 200 ;

- cinq stations au maximum ;

- présence des identifiants et noms de station.



Statut :



`Validé`



### RF-04 - Station inexistante



Objectif :



Vérifier la gestion d'une ressource inconnue.



Action :



Appeler une station inexistante.



Résultat attendu :



- code HTTP 404 ;

- message `Station introuvable`.



Statut :



`Validé`



### RF-05 - Orchestration Airflow



Objectif :



Vérifier l'exécution automatisée du pipeline Data.



Chaîne testée :



`ingestion\_velib -> load\_star\_schema -> spark\_transformation`



Résultat attendu :



Les trois tâches terminent avec le statut `success`.



Statut :



`Validé`



## 3. Tests structurels



### RS-01 - Présence de la base analytique



Objectif :



Vérifier que la base `velops\_star.db` est disponible après transformation.



Résultat attendu :



Le fichier existe.



Statut :



`Validé`



### RS-02 - Intégrité des clés étrangères



Objectif :



Vérifier l'intégrité du schéma en étoile.



Contrôle SQLite :



`PRAGMA foreign\_key\_check`



Résultat attendu :



Aucune anomalie.



Statut :



`Validé`



### RS-03 - Table de faits non vide



Objectif :



Vérifier que les observations sont chargées dans le modèle analytique.



Résultat attendu :



`COUNT(\*) > 0`



dans :



`fait\_disponibilite`



Statut :



`Validé`



### RS-04 - Dimensions non vides



Objectif :



Vérifier que les dimensions sont alimentées.



Tables concernées :



- `dim\_station`

- `dim\_temps`

- `dim\_arrondissement`



Résultat attendu :



Chaque dimension contient des données.



Statut :



`Validé`



### RS-05 - Tests dbt



Objectif :



Vérifier la qualité des transformations analytiques.



Tests exécutés :



- `not\_null`

- `unique`



Résultat observé :



`8 tests PASS`



Statut :



`Validé`



### RS-06 - Tests pytest



Objectif :



Vérifier les composants API et base de données.



Résultat observé :



`9 tests PASS`



Statut :



`Validé`



## 4. Tests de sécurité



### SEC-01 - Non-versionnement des secrets



Objectif :



Vérifier que le fichier `.env` n'est pas suivi par Git.



Contrôle :



`git ls-files .env`



Résultat attendu :



Aucune sortie.



Statut :



`Validé`



### SEC-02 - Non-versionnement des bases locales



Objectif :



Éviter la publication involontaire des données locales.



Fichiers ignorés :



- `\*.db`

- `\*.sqlite`

- `\*.sqlite3`



Statut :



`Validé`



### SEC-03 - Non-versionnement du modèle ML



Objectif :



Éviter de versionner les artefacts binaires locaux.



Fichiers ignorés :



- `\*.pkl`

- `\*.joblib`



Statut :



`Validé`



### SEC-04 - Gestion des ressources inexistantes



Objectif :



Vérifier qu'une ressource inconnue ne provoque pas une erreur serveur.



Résultat attendu :



Une station inconnue retourne HTTP 404 et non HTTP 500.



Statut :



`Validé`



### SEC-05 - Contrôle CI/CD



Objectif :



Vérifier qu'une modification du code déclenche les contrôles automatisés avant intégration.



Contrôles GitHub Actions :



- installation des dépendances ;

- compilation Python ;

- génération des données de test ;

- construction du modèle en étoile ;

- entraînement ML ;

- tests pytest ;

- construction de l'image Docker.



Résultat observé :



Workflow `VelOps CI` terminé avec le statut `Success`.



Statut :



`Validé`



## 5. Supervision et disponibilité



### SUP-01 - Collecte Prometheus



Objectif :



Vérifier que Prometheus collecte les métriques FastAPI.



Target :



`velops-api`



Résultat attendu :



`UP`



Statut :



`Validé`



### SUP-02 - Dashboard Grafana



Objectif :



Vérifier la visualisation des indicateurs opérationnels.



Dashboard :



`VelOps - Supervision API`



Indicateurs :



- disponibilité API ;

- débit ;

- latence P99 ;

- taux d'erreurs HTTP 5xx ;

- codes HTTP ;

- volume des requêtes.



Statut :



`Validé`



### SUP-03 - Règles d'alerte



Règles configurées :



- `VelOpsAPIDown`

- `VelOpsHighLatency`

- `VelOpsHighErrorRate`



Statut :



`Validé`



## 6. Critères d'acceptation



Le prototype est considéré comme recevable lorsque :



- les tests pytest sont réussis ;

- les tests dbt sont réussis ;

- l'intégrité relationnelle est respectée ;

- le pipeline Airflow termine avec succès ;

- l'image Docker peut être construite ;

- la CI GitHub Actions est verte ;

- Prometheus détecte l'API comme disponible ;

- Grafana affiche les métriques ;

- les règles d'alerte sont chargées.



## 7. Conclusion de recette



Les tests réalisés confirment le bon fonctionnement du prototype local VelOps sur les composants implémentés.



Les services Cloud mentionnés dans l'architecture cible, notamment AWS S3, EMR, MWAA et Snowflake, ne font pas partie de cette recette locale et restent des composants prévus pour une industrialisation future.



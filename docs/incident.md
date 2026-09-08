# VelOps Paris - Procédure de Gestion d'Incident



## 1. Objectif



Cette procédure décrit la méthode utilisée pour détecter, diagnostiquer, corriger et documenter un incident affectant l'infrastructure Data VelOps.



Elle s'applique aux composants suivants :



- ingestion Python ;

- base SQLite ;

- modèle analytique ;

- Spark ;

- Airflow ;

- dbt ;

- FastAPI ;

- Docker ;

- Prometheus ;

- Grafana ;

- GitHub Actions.



## 2. Cycle de gestion d'un incident



La démarche appliquée est la suivante :



1. détecter l'incident ;

2. qualifier son impact ;

3. identifier le composant concerné ;

4. collecter les logs et métriques ;

5. formuler une hypothèse de cause ;

6. reproduire l'erreur ;

7. appliquer une correction ;

8. exécuter les tests de non-régression ;

9. vérifier le retour à la normale ;

10. documenter l'incident.



## 3. Exemple réel : échec d'exécution d'un DAG Airflow



### Contexte



Lors de l'industrialisation du pipeline VelOps avec Apache Airflow, le DAG était correctement détecté par Airflow, mais les tâches échouaient au moment de leur exécution.



Le pipeline concerné était :



`ingestion\_velib -> load\_star\_schema -> spark\_transformation`



### Symptôme initial



Le DAG apparaissait dans l'interface Airflow mais une tâche passait en échec au lancement.



Les logs du scheduler indiquaient une erreur de connexion vers l'Execution API interne d'Airflow.



### Diagnostic



L'analyse des logs a permis d'identifier plusieurs causes successives :



- l'URL de l'Execution API pointait vers `localhost` depuis le conteneur scheduler ;

- dans un environnement Docker, `localhost` désignait le conteneur lui-même et non le service API Airflow ;

- après correction de l'URL, une erreur d'authentification JWT est apparue ;

- le traitement Spark utilisait ensuite un chemin Python spécifique à Windows, incompatible avec le conteneur Linux Airflow.



### Cause racine



L'incident provenait d'une mauvaise adaptation entre l'environnement local Windows et l'environnement d'exécution Docker Linux.



Trois éléments de configuration étaient concernés :



1. l'URL de l'Execution API ;

2. la configuration JWT partagée entre les services Airflow ;

3. le chemin de l'interpréteur Python utilisé par PySpark.



## 4. Corrections appliquées



### Correction de l'Execution API



La configuration Airflow a été modifiée pour utiliser l'adresse réseau Docker du service API :



`http://airflow-api-server:8080/execution/`



### Correction de l'authentification



Une clé JWT commune a été configurée sur les services Airflow concernés afin de permettre les échanges entre composants.



Dans une architecture de production, cette clé doit être stockée dans un gestionnaire de secrets et ne doit pas être codée en dur dans le dépôt.



### Correction Spark



Le script Spark a été rendu portable en utilisant :



`sys.executable`



au lieu d'un chemin Python Windows fixe.



Les variables suivantes sont ensuite configurées dynamiquement :



- `PYSPARK\_PYTHON`

- `PYSPARK\_DRIVER\_PYTHON`



Cette modification permet au même script de fonctionner sous Windows et dans un conteneur Linux.



## 5. Validation après correction



Après application des corrections :



- le DAG est détecté sans erreur d'import ;

- le DAG peut être déclenché manuellement ;

- la tâche d'ingestion s'exécute avec succès ;

- le chargement du modèle en étoile s'exécute avec succès ;

- le traitement Spark s'exécute avec succès ;

- l'état final du DAG est `success`.



Un run complet a validé l'enchaînement :



`ingestion\_velib -> load\_star\_schema -> spark\_transformation`



## 6. Mesures préventives



Afin de réduire le risque de réapparition de cet incident :



- éviter les chemins absolus propres à un système d'exploitation ;

- utiliser des variables d'environnement ;

- centraliser les secrets ;

- tester les images Docker avant déploiement ;

- vérifier la résolution DNS entre services Docker ;

- exécuter les tests automatisés ;

- contrôler les logs Airflow après chaque modification ;

- maintenir une documentation de configuration.



## 7. Classification de l'incident



Type :



`Incident d'intégration / configuration`



Impact :



`Blocage du pipeline orchestré`



Criticité :



`Haute pendant la phase de déploiement`



Résolution :



`Configuration réseau, authentification et portabilité Spark corrigées`



Statut final :



`Résolu`



## 8. Retour d'expérience



Cet incident a montré que la réussite d'un pipeline local ne garantit pas son fonctionnement dans un environnement conteneurisé.



La portabilité, la gestion des secrets, la communication inter-services et les différences entre systèmes d'exploitation doivent être intégrées dès la conception de l'infrastructure.



# VelOps Paris - Plan de Maintien en Condition Opérationnelle



## 1. Objectif



Le maintien en condition opérationnelle (MCO) du projet VelOps vise à garantir la disponibilité, la fiabilité, la sécurité et la maintenabilité de l'infrastructure Data et de l'API de prédiction.



Le périmètre comprend :



- les pipelines d'ingestion ;

- la base de données analytique ;

- les traitements Spark ;

- l'orchestration Airflow ;

- les transformations dbt ;

- l'API FastAPI ;

- la conteneurisation Docker ;

- la supervision Prometheus / Grafana ;

- les workflows CI/CD GitHub Actions.



## 2. Supervision opérationnelle



Les principaux indicateurs supervisés sont :



- disponibilité de l'API ;

- débit des requêtes ;

- latence P99 ;

- taux d'erreurs HTTP 5xx ;

- état du target Prometheus ;

- échec des DAG Airflow ;

- intégrité des données ;

- succès des tests automatisés CI/CD.



Les métriques FastAPI sont exposées via :



`/metrics`



Prometheus collecte ces métriques toutes les 5 secondes.



Grafana permet leur visualisation dans le dashboard :



`VelOps - Supervision API`



## 3. Seuils de surveillance



### Disponibilité API



Condition critique :



`up{job="velops-api"} == 0`



Durée avant alerte :



30 secondes.



### Latence API



Objectif :



P99 inférieur à 100 ms.



Une alerte de niveau warning est déclenchée lorsque la latence P99 dépasse 100 ms pendant plus d'une minute.



### Taux d'erreurs



Objectif :



taux d'erreurs HTTP 5xx inférieur à 5 %.



Une alerte critique est déclenchée lorsque ce seuil est dépassé pendant plus d'une minute.



## 4. Maintenance préventive



Fréquence recommandée : hebdomadaire.



Actions :



- vérifier l'état des conteneurs Docker ;

- consulter les dashboards Grafana ;

- vérifier les erreurs Airflow ;

- contrôler les logs ;

- exécuter les tests pytest ;

- exécuter les tests dbt ;

- contrôler l'intégrité SQLite ;

- vérifier la consommation disque ;

- vérifier les versions des dépendances Python ;

- vérifier l'état du pipeline GitHub Actions.



## 5. Maintenance corrective



En cas d'incident :



1. identifier le composant en erreur ;

2. analyser les métriques et les logs ;

3. reproduire l'erreur ;

4. isoler la cause ;

5. appliquer une correction ;

6. exécuter les tests ;

7. redéployer si nécessaire ;

8. vérifier le retour à la normale ;

9. documenter l'incident.



## 6. Sauvegarde



Les éléments à sauvegarder sont :



- code source Git ;

- fichiers de configuration ;

- schémas SQL ;

- modèles dbt ;

- configuration Airflow ;

- dashboards Grafana ;

- règles Prometheus ;

- scripts Spark ;

- modèles ML ;

- bases de données lorsqu'elles contiennent des données persistantes utiles.



Le dépôt GitHub constitue la référence pour le code et les configurations versionnées.



## 7. Mise à jour des dépendances



Avant toute montée de version :



1. créer une branche dédiée ;

2. mettre à jour la dépendance ;

3. exécuter les tests locaux ;

4. vérifier le pipeline GitHub Actions ;

5. valider l'image Docker ;

6. fusionner uniquement si tous les contrôles passent.



## 8. Continuité de service



En cas d'indisponibilité d'un composant :



- identifier la dépendance concernée ;

- redémarrer uniquement le service impacté ;

- conserver les autres services opérationnels ;

- vérifier l'état de l'API ;

- vérifier la collecte Prometheus ;

- valider le retour à l'état nominal dans Grafana.



## 9. Améliorations futures



Pour une mise en production Cloud, les évolutions prévues sont :



- stockage Bronze sur AWS S3 ;

- traitement Spark sur AWS EMR ;

- orchestration Airflow via AWS MWAA ;

- stockage analytique Snowflake ;

- transformations dbt sur Snowflake ;

- gestion centralisée des secrets ;

- haute disponibilité ;

- sauvegardes automatisées ;

- notifications Alertmanager ;

- déploiement Infrastructure as Code avec Terraform.



Ces composants correspondent à l'architecture cible et ne sont pas tous déployés dans le prototype local actuel.



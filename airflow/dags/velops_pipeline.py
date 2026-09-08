from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


with DAG(
    dag_id="velops_pipeline",
    description="Pipeline VelOps : ingestion, modèle en étoile et traitement Spark",
    start_date=datetime(2026, 9, 1),
    schedule="0 2 * * *",
    catchup=False,
    tags=["velops", "data-engineering"],
) as dag:

    ingestion_velib = BashOperator(
        task_id="ingestion_velib",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/ingestion/pipeline.py"
        ),
    )

    load_star_schema = BashOperator(
        task_id="load_star_schema",
        bash_command=(
            "cd /opt/airflow/project && "
            "python src/transformation/load_star_schema.py"
        ),
    )

    spark_transformation = BashOperator(
        task_id="spark_transformation",
        bash_command=(
            "cd /opt/airflow/project && "
            "python spark/transform_velops.py"
        ),
    )

    ingestion_velib >> load_star_schema >> spark_transformation
import os
import sqlite3
import sys
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    count,
    max as spark_max,
    min as spark_min,
    round as spark_round,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DB = PROJECT_ROOT / "velops_paris.db"
OUTPUT_DIR = PROJECT_ROOT / "spark" / "output"


def load_source_data():
    with sqlite3.connect(SOURCE_DB) as conn:
        cursor = conn.execute(
            """
            SELECT
                id,
                nom,
                velos_dispo,
                places_libres,
                id_arrondissement,
                date_ingestion
            FROM stations
            """
        )

        rows = cursor.fetchall()

    return rows


def main():
    print("=== VELOPS - TRAITEMENT SPARK ===")

    python_executable = str(
        PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    )

    os.environ["PYSPARK_PYTHON"] = python_executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = python_executable

    print(f"[CONFIG] Python Spark : {python_executable}")

    spark = (
        SparkSession.builder
        .appName("VelOpsDistributedProcessing")
        .master("local[*]")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    try:
        rows = load_source_data()

        print(f"[1/4] Lignes extraites de SQLite : {len(rows)}")

        columns = [
            "station_id",
            "nom_station",
            "velos_disponibles",
            "places_libres",
            "arrondissement_id",
            "date_ingestion",
        ]

        df = spark.createDataFrame(rows, columns)

        print(
            f"[2/4] DataFrame Spark créé : "
            f"{df.count()} lignes"
        )

        df_clean = (
            df
            .filter(col("station_id").isNotNull())
            .filter(col("velos_disponibles") >= 0)
            .filter(col("places_libres") >= 0)
            .dropDuplicates(
                [
                    "station_id",
                    "date_ingestion",
                ]
            )
        )

        print(
            f"[3/4] Lignes après nettoyage : "
            f"{df_clean.count()}"
        )

        df_stats = (
            df_clean
            .groupBy("arrondissement_id")
            .agg(
                count("*").alias("nombre_observations"),
                spark_round(
                    avg("velos_disponibles"),
                    2,
                ).alias("moyenne_velos"),
                spark_round(
                    avg("places_libres"),
                    2,
                ).alias("moyenne_places_libres"),
                spark_min(
                    "velos_disponibles"
                ).alias("minimum_velos"),
                spark_max(
                    "velos_disponibles"
                ).alias("maximum_velos"),
            )
            .orderBy("arrondissement_id")
        )

        print(
            "[4/4] Agrégation distribuée "
            "par arrondissement :"
        )

        df_stats.show(truncate=False)

        OUTPUT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = (
            OUTPUT_DIR / "stats_arrondissements.csv"
        )

        resultats = df_stats.collect()

        with open(
            output_path,
            "w",
            encoding="utf-8",
            newline="",
        ) as fichier:
            fichier.write(
                "arrondissement_id,"
                "nombre_observations,"
                "moyenne_velos,"
                "moyenne_places_libres,"
                "minimum_velos,"
                "maximum_velos\n"
            )

            for row in resultats:
                fichier.write(
                    f"{row['arrondissement_id']},"
                    f"{row['nombre_observations']},"
                    f"{row['moyenne_velos']},"
                    f"{row['moyenne_places_libres']},"
                    f"{row['minimum_velos']},"
                    f"{row['maximum_velos']}\n"
                )

        print()
        print(
            "[OK] Résultats Spark enregistrés dans : "
            f"{output_path}"
        )

    finally:
        spark.stop()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[ERREUR] {exc}")
        sys.exit(1)
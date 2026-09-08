import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_DB = PROJECT_ROOT / "velops_paris.db"
TARGET_DB = PROJECT_ROOT / "velops_star.db"
SCHEMA_FILE = PROJECT_ROOT / "sql" / "schema.sql"


def main():
    print("=== VELOPS - CHARGEMENT DU MODELE EN ETOILE ===")

    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Base source introuvable : {SOURCE_DB}")

    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(f"Schéma SQL introuvable : {SCHEMA_FILE}")

    target_conn = sqlite3.connect(TARGET_DB)

    try:
        target_conn.execute("PRAGMA foreign_keys = ON")

        # Attachement de la base opérationnelle en lecture
        target_conn.execute(
            "ATTACH DATABASE ? AS main_source",
            (str(SOURCE_DB),)
        )

        schema_sql = SCHEMA_FILE.read_text(encoding="utf-8-sig")
        target_conn.executescript(schema_sql)

        tables_cibles = target_conn.execute(
            """
            SELECT name
            FROM main.sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

        print("[1/4] Schéma analytique créé.")
        print(f"      Tables cibles : {tables_cibles}")

        # ============================================================
        # DIMENSION ARRONDISSEMENT
        # ============================================================

        arrondissements = target_conn.execute(
            """
            SELECT DISTINCT
                id_arrondissement,
                nom
            FROM main_source.arrondissements
            WHERE id_arrondissement IS NOT NULL
            """
        ).fetchall()

        target_conn.executemany(
            """
            INSERT OR IGNORE INTO dim_arrondissement (
                arrondissement_id,
                nom_arrondissement
            )
            VALUES (?, ?)
            """,
            arrondissements,
        )

        print(f"[2/4] Arrondissements chargés : {len(arrondissements)}")
        target_conn.execute(
            """
            UPDATE dim_arrondissement
            SET nom_arrondissement = REPLACE(
                nom_arrondissement,
                char(160),
                ' '
            )
            """
        )
        # ============================================================
        # DIMENSION STATION
        # ============================================================

        stations = target_conn.execute(
            """
            SELECT
                id,
                MAX(nom)
            FROM main_source.stations
            WHERE id IS NOT NULL
            GROUP BY id
            """
        ).fetchall()

        target_conn.executemany(
            """
            INSERT OR IGNORE INTO dim_station (
                station_id,
                nom_station
            )
            VALUES (?, ?)
            """,
            stations,
        )

        print(f"[3/4] Stations chargées : {len(stations)}")

        # ============================================================
        # DIMENSION TEMPS
        # ============================================================

        dates = target_conn.execute(
            """
            SELECT DISTINCT date_ingestion
            FROM main_source.stations
            WHERE date_ingestion IS NOT NULL
            ORDER BY date_ingestion
            """
        ).fetchall()

        for (date_ingestion,) in dates:
            target_conn.execute(
                """
                INSERT OR IGNORE INTO dim_temps (
                    date_complete,
                    annee,
                    mois,
                    jour,
                    heure,
                    minute
                )
                VALUES (
                    ?,
                    CAST(strftime('%Y', ?) AS INTEGER),
                    CAST(strftime('%m', ?) AS INTEGER),
                    CAST(strftime('%d', ?) AS INTEGER),
                    CAST(strftime('%H', ?) AS INTEGER),
                    CAST(strftime('%M', ?) AS INTEGER)
                )
                """,
                (
                    date_ingestion,
                    date_ingestion,
                    date_ingestion,
                    date_ingestion,
                    date_ingestion,
                    date_ingestion,
                ),
            )

        # ============================================================
        # TABLE DE FAITS
        # ============================================================

        target_conn.execute("DELETE FROM fait_disponibilite")

        target_conn.execute(
            """
            INSERT INTO fait_disponibilite (
                station_id,
                arrondissement_id,
                temps_id,
                velos_disponibles,
                places_libres
            )
            SELECT
                s.id,
                s.id_arrondissement,
                dt.temps_id,
                s.velos_dispo,
                s.places_libres
            FROM main_source.stations AS s
            JOIN dim_temps AS dt
                ON dt.date_complete = s.date_ingestion
            """
        )

        target_conn.commit()

        print("[4/4] Table de faits chargée.")

        # ============================================================
        # CONTROLES
        # ============================================================

        nb_stations = target_conn.execute(
            "SELECT COUNT(*) FROM dim_station"
        ).fetchone()[0]

        nb_arrondissements = target_conn.execute(
            "SELECT COUNT(*) FROM dim_arrondissement"
        ).fetchone()[0]

        nb_temps = target_conn.execute(
            "SELECT COUNT(*) FROM dim_temps"
        ).fetchone()[0]

        nb_faits = target_conn.execute(
            "SELECT COUNT(*) FROM fait_disponibilite"
        ).fetchone()[0]

        print("\n=== CONTROLE DU CHARGEMENT ===")
        print(f"dim_station          : {nb_stations}")
        print(f"dim_arrondissement   : {nb_arrondissements}")
        print(f"dim_temps            : {nb_temps}")
        print(f"fait_disponibilite   : {nb_faits}")

    finally:
        target_conn.close()


if __name__ == "__main__":
    main()

import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "velops_paris.db"


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.executescript(
            """
            CREATE TABLE stations (
                id_enregistrement INTEGER PRIMARY KEY AUTOINCREMENT,
                id TEXT,
                nom TEXT,
                velos_dispo INTEGER,
                places_libres INTEGER,
                id_arrondissement INTEGER,
                date_ingestion TEXT
            );

            CREATE TABLE arrondissements (
                id_arrondissement INTEGER PRIMARY KEY,
                nom TEXT,
                description TEXT,
                date_ingestion TEXT
            );
            """
        )

        arrondissements = [
            (
                1,
                "1er arrondissement",
                "Arrondissement de test CI",
                "2026-09-08 10:00:00",
            ),
            (
                2,
                "2e arrondissement",
                "Arrondissement de test CI",
                "2026-09-08 10:00:00",
            ),
            (
                3,
                "3e arrondissement",
                "Arrondissement de test CI",
                "2026-09-08 10:00:00",
            ),
        ]

        conn.executemany(
            """
            INSERT INTO arrondissements (
                id_arrondissement,
                nom,
                description,
                date_ingestion
            )
            VALUES (?, ?, ?, ?)
            """,
            arrondissements,
        )

        stations = []

        for index in range(1, 31):
            arrondissement = ((index - 1) % 3) + 1
            velos = (index * 3) % 25
            places = 30 - velos

            stations.append(
                (
                    f"CI{index:03d}",
                    f"Station CI {index}",
                    velos,
                    places,
                    arrondissement,
                    f"2026-09-08 10:{index:02d}:00",
                )
            )

        conn.executemany(
            """
            INSERT INTO stations (
                id,
                nom,
                velos_dispo,
                places_libres,
                id_arrondissement,
                date_ingestion
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            stations,
        )

        conn.commit()

        print(
            f"Base CI créée avec succès : "
            f"{len(stations)} observations"
        )

    finally:
        conn.close()


if __name__ == "__main__":
    main()
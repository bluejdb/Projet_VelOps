-- ============================================================
-- VELOPS PARIS - BLOC 4
-- Modèle analytique en étoile
-- ============================================================

PRAGMA foreign_keys = ON;


-- ============================================================
-- DIMENSION : STATION
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_station (
    station_id TEXT PRIMARY KEY,
    nom_station TEXT NOT NULL
);


-- ============================================================
-- DIMENSION : ARRONDISSEMENT
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_arrondissement (
    arrondissement_id INTEGER PRIMARY KEY,
    nom_arrondissement TEXT NOT NULL
);


-- ============================================================
-- DIMENSION : TEMPS
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_temps (
    temps_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_complete TEXT NOT NULL UNIQUE,
    annee INTEGER,
    mois INTEGER,
    jour INTEGER,
    heure INTEGER,
    minute INTEGER
);


-- ============================================================
-- TABLE DE FAITS : DISPONIBILITE
-- ============================================================

CREATE TABLE IF NOT EXISTS fait_disponibilite (
    disponibilite_id INTEGER PRIMARY KEY AUTOINCREMENT,

    station_id TEXT NOT NULL,
    arrondissement_id INTEGER,
    temps_id INTEGER NOT NULL,

    velos_disponibles INTEGER NOT NULL,
    places_libres INTEGER NOT NULL,

    FOREIGN KEY (station_id)
        REFERENCES dim_station(station_id),

    FOREIGN KEY (arrondissement_id)
        REFERENCES dim_arrondissement(arrondissement_id),

    FOREIGN KEY (temps_id)
        REFERENCES dim_temps(temps_id),

    CHECK (velos_disponibles >= 0),
    CHECK (places_libres >= 0)
);


-- ============================================================
-- INDEX
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fait_station
ON fait_disponibilite(station_id);

CREATE INDEX IF NOT EXISTS idx_fait_arrondissement
ON fait_disponibilite(arrondissement_id);

CREATE INDEX IF NOT EXISTS idx_fait_temps
ON fait_disponibilite(temps_id);

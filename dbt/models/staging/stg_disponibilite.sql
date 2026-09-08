select
    station_id,
    arrondissement_id,
    temps_id,
    velos_disponibles,
    places_libres,
    velos_disponibles + places_libres as capacite_station,
    case
        when velos_disponibles + places_libres = 0 then 0
        else round(
            velos_disponibles * 100.0
            / (velos_disponibles + places_libres),
            2
        )
    end as taux_disponibilite
from sqlite_scan(
    '{{ env_var("VELOPS_STAR_DB_PATH") }}',
    'fait_disponibilite'
)
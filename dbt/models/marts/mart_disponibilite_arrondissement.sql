select
    arrondissement_id,
    count(*) as nombre_observations,
    round(avg(velos_disponibles), 2) as moyenne_velos,
    round(avg(places_libres), 2) as moyenne_places_libres,
    round(avg(capacite_station), 2) as capacite_moyenne,
    round(avg(taux_disponibilite), 2) as taux_disponibilite_moyen,
    min(velos_disponibles) as minimum_velos,
    max(velos_disponibles) as maximum_velos
from {{ ref('stg_disponibilite') }}
group by arrondissement_id
order by arrondissement_id
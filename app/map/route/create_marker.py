import os
import folium
from fastapi import APIRouter
from pydantic import BaseModel

from app.logs import map_logger

class Coord(BaseModel):
    lat: float
    long: float
    
router = APIRouter(prefix="/map_create_marker")

user_points: list[str] = []


# INSERTION CODE HTML
# Détection d'emplacement de nom dans le fichier HTML Folium.
def find_variable_name(html, name_start) -> str:
    variable_pattern = "var "
    pattern = variable_pattern + name_start

    starting_index = html.find(pattern) + len(variable_pattern)
    tmp_html = html[starting_index:]
    ending_index = tmp_html.find(" =") + starting_index

    return html[starting_index:ending_index]


# INSERTION CODE HTML
# Détection de l'emplacement pour la création de 'LatLong' dans le fichier HTML Folium.
def find_latlong_indices(html) -> tuple[int, int]:
    
    pattern = "function latLngPop(e)"
    starting_index = html.find(pattern)
    tmp_html = html[starting_index:]

    found = 0
    index = 0
    opening_found = False

    while not opening_found or found > 0:
        if tmp_html[index] == "{":
            found += 1
            opening_found = True
        elif tmp_html[index] == "}":
            found -= 1

        index += 1

    ending_index = starting_index + index

    return starting_index, ending_index


# INSERTION CODE HTML
# Rédaction du code à insérer pour créer un 'marker' par l'utilisateur.
# Un 'clic' sur le marker créé permet son effacement instantané.
#['e=>e.target.remove();' à indiquer si on ne met pas de function(e)]
def html_code(latlong_name: str, map_name: str) -> str:
    return '''
            // custom code
            function latLngPop(e) {
                %s
                    .setLatLng(e.latlng)
                    .setContent("Étape ajoutée 👍")
                    .openOn(%s);

                L.marker(
                    [`${e.latlng.lat}`,`${e.latlng.lng}`],
                    {}
                ).addTo(%s).on('click', function(e) {
                                            fetch('http://localhost:5003/map_create_marker/remove_user_point', {
                                                        method: 'POST',
                                                        headers: {
                                                            'Accept': 'application/json',
                                                            'Content-Type': 'application/json'
                                                        },
                                                        body: JSON.stringify({
                                                            lat: `${e.latlng.lat}`,
                                                            long: `${e.latlng.lng}`
                                                        })
                                            });
                                            e.target.remove();
                                        });

                fetch('http://localhost:5003/map_create_marker/add_user_point', {
                            method: 'POST',
                            headers: {
                                'Accept': 'application/json',
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                lat: `${e.latlng.lat}`,
                                long: `${e.latlng.lng}`
                            })
                        });
            }
            // end custom code
    ''' % (latlong_name, map_name, map_name)


def insert_html_code_for_marker(html_file_path: str) -> None:
    html_folium = None

    map_logger.info("Insertion du code HTML pour création de 'markers'")

    with open(html_file_path, 'r') as mapfile:
        html_folium = mapfile.read()

    map_variable_name = find_variable_name(html_folium, "map_")
    popup_variable_name = find_variable_name(html_folium, "lat_lng_popup_")

    ind_start, ind_end = find_latlong_indices(html_folium)

    with open(html_file_path, 'w') as mapfile:
        mapfile.write(
            html_folium[:ind_start] + \
            html_code(popup_variable_name, map_variable_name) + \
            html_folium[ind_end:]
        )


# AJOUT POI GÉOGRAPHIQUE DE L'UTILISATEUR
@router.post("/add_user_point")
def add_user_point(coordinates:Coord) -> None:
    map_logger.info("Ajout POI géographique")

    global user_points
    user_points.append([coordinates.lat,coordinates.long])


# SUPPRESSION POI GÉOGRAPHIQUE DE L'UTILISATEUR
@router.post("/remove_user_point")
def remove_user_point(coordinates:Coord) -> None:
    map_logger.info("Suppression POI géographique")

    global user_points
    elt = [coordinates.lat,coordinates.long]
    if elt in user_points: user_points.remove(elt)


# ENVOI LISTE DES MARKERS CRÉÉS
@router.get("/get_user_points")
def get_user_points() -> list[Coord]:
    map_logger.info("Envoi liste des points géographiques créés")

    return user_points


# REMISE PAR DÉFAUT DES POINTS GÉOGRAPHIQUES DE L'UTILISATEUR
@router.post("/clean_user_points")
def clean_user_points() -> None:
    map_logger.info("Initialisation dela liste des POI géographiques")
    global user_points
    
    user_points.clear()


if __name__ == "__main__":
    test = "hello"

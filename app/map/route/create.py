from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from geopy.geocoders import ArcGIS
import os
import folium

import openrouteservice
from openrouteservice import convert

router = APIRouter(prefix="/map_create")

class Coord(BaseModel):
    lat: float
    long: float
    
steps=[] # 'poi' pour trajet en couples (LAT, LONG)
routes=[] # 'poi' pour trajet en couples (LONG, LAT)

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_FILE_PATH = os.path.dirname((FILE_PATH))
FILES_PATH = PARENT_FILE_PATH + '/files'
ROUTE_FILE_PATH = FILES_PATH + '/folium-map.html'

# INSERTION CODE HTML
# Détection du nom du plan Folium.
def find_map_variable_name(html_file) -> str:
    pattern = "var map_"

    starting_index = html_file.find(pattern) + 4
    tmp_html = html_file[starting_index:]
    ending_index = tmp_html.find(" =") + starting_index

    return html_file[starting_index:ending_index]


# INSERTION CODE HTML
# Détection du début d'insertion de code.
def find_start_index(html_file) -> int:
    pattern = f"""
                </script></html>
                """
    starting_index = html_file.find(pattern) - 16

    return starting_index


# INSERTION CODE HTML
# Rédaction du code à insérer dans chaque 'popup'.
def html_code(points, map_id) -> str:
    return '''
            var poly_line_60b609109ba1e9727feeb322482f7103 = L.polyline(
                %s,
                {"bubblingMouseEvents": true,
                "color": "blue",
                "dashArray": null,
                "dashOffset": null,
                "fill": false,
                "fillColor": "blue",
                "fillOpacity": 0.2,
                "fillRule": "evenodd",
                "lineCap": "round",
                "lineJoin": "round",
                "noClip": false,
                "opacity": 0.7,
                "smoothFactor": 1.0,
                "stroke": true,
                "weight": 5}
            ).addTo(%s);
</script>
</html>''' % (points,map_id)


# CRÉATION DE ROUTE
# Ajout des coordonnées du 'poi'.
@router.post("/poi_add")
def add_step(coordinates: Coord):
    poi_coord_steps = (coordinates.lat, coordinates.long)
    if poi_coord_steps not in steps: steps.append(poi_coord_steps)

    poi_coord_routes = (coordinates.long, coordinates.lat)
    if poi_coord_routes not in routes: routes.append(poi_coord_routes)

    return steps, routes


# CRÉATION DE ROUTE
# Suppression des coordonnées du 'poi'.
@router.post("/poi_remove")
def remove_step(coordinates: Coord):
    poi_coord_steps = (coordinates.lat, coordinates.long)
    if poi_coord_steps in steps: steps.remove(poi_coord_steps)

    poi_coord_routes = (coordinates.long, coordinates.lat)
    if poi_coord_routes in routes: routes.remove(poi_coord_routes)

    return steps, routes


# CRÉATION DE ROUTE
# Création de route avec la liste des 'poi' créée.
@router.post("/route_create")
def create_route():# -> bool | FileResponse:

    if len(routes) <= 1: return False

    ORS_KEY = '5b3ce3597851110001cf62488dbf498826f54bbb859dd1aa67054989'
    client = openrouteservice.Client(key=ORS_KEY)
    route = client.directions(coordinates=routes, profile='driving-car')
    decode = convert.decode_polyline(route['routes'][0]['geometry'])

    mini_steps = [[lat, lon] for lon, lat in decode['coordinates']]

    html = None

    with open(ROUTE_FILE_PATH, 'r') as mapfile:
        html = mapfile.read()

    map_name = find_map_variable_name(html)
    start_index = find_start_index(html)

    # Injection du code à la fin du fichier HTML.
    with open(ROUTE_FILE_PATH, 'w') as mapfile:
        mapfile.write(
            html[:start_index] + \
                html_code(mini_steps, map_name)
        )
    return FileResponse(ROUTE_FILE_PATH,
                        media_type='text/html')


# CONVERSION ADRESSE -> COORDONNÉES (LAT, LONG)
# Conversion adresse de départ avec insertion de ces coordonnées
# en début de liste après effacement des anciennes données.
@router.post("/addr_to_coord_departure")
def insert_departure_coord(addr: str) -> bool:
    global steps
    global routes

    addr_departure = addr
    location = ArcGIS().geocode(addr_departure)
    addr_departure_lat = str(location.latitude)
    addr_departure_long = str(location.longitude)

    steps = [(addr_departure_lat,
              addr_departure_long)]
    routes = [(addr_departure_long,
               addr_departure_lat)]

    return True


# CONVERSION ADRESSE -> COORDONNÉES (LAT, LONG)
# Conversion adresse d'arrivée avec insertion de ces coordonnées
# en fin de liste.
@router.post("/addr_to_coord_arrival")
def insert_arrival_coord(addr: str) -> bool:
    global steps
    global routes

    addr_arrival = addr
    location = ArcGIS().geocode(addr_arrival)
    addr_arrival_lat = str(location.latitude)
    addr_arrival_long = str(location.longitude)

    steps.append((addr_arrival_lat,
                  addr_arrival_long))
    routes.append((addr_arrival_long,
                   addr_arrival_lat))
    
    return True

if __name__ == "__main__":
    test = "hello"

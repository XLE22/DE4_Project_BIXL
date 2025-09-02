import os
import pandas as pd
import requests

from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel
from geopy.geocoders import ArcGIS

import openrouteservice
from openrouteservice import convert

from app.main import HTML_ADDR_DEP_ID, HTML_ADDR_ARR_ID
from .create_marker import user_points

router = APIRouter(prefix="/map_create")

is_departure: bool = False
is_arrival: bool = False

class ReportStep:
    def __init__(self, name, elt) -> None:
        self.name = name
        self.coord = (elt[0],elt[1])

    def __eq__(self, other) -> bool:
        if self.name == other.name:
            return (self.coord[0] == other.coord[0]) and\
                    (self.coord[1] == other.coord[1])
        return False

departure = ReportStep("",["",""])
arrival = ReportStep("",["",""])

class Coord(BaseModel):
    id: int
    lat: float
    long: float
    
steps: list[ReportStep] = [] # 'poi' pour trajet en ReportStep (LAT, LONG)
routes: list[ReportStep] = [] # 'poi' pour trajet en ReportStep (LONG, LAT)

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_FILE_PATH = os.path.dirname((FILE_PATH))
FILES_PATH = PARENT_FILE_PATH + '/files'
ROUTE_FILE_PATH = FILES_PATH + '/folium-map.html'

DEPARTURE_REPORT = "DÉPART"#"Départ"
ARRIVAL_REPORT = "ARRIVÉE"#"Arrivée"
STEP_REPORT = "ÉTAPE "#"Étape"

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
    starting_index = html_file.find(pattern) - 7 #Pour insérer le code entre les deux tags spécifiés en 'pattern'

    return starting_index


# INSERTION CODE HTML
# Rédaction du code à insérer dans chaque 'popup'.
def html_code(points, map_id) -> str:
    return '''<script>
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


# TEMPS DE TRAJET
# Estimation du temps de trajet voiture entre deux points géographiques AVEC format.
def calculate_time(depart: ReportStep, arriv: ReportStep) -> str:
    ROUTES = 'routes'
    SUMMARY = 'summary'
    DURATION = 'duration'

    ORS_KEY = '5b3ce3597851110001cf62488dbf498826f54bbb859dd1aa67054989'
    client = openrouteservice.Client(key=ORS_KEY) 

    route=client.directions(coordinates=[depart.coord, arriv.coord],
                            profile='driving-car')
    
    res_mn = int(route[ROUTES][0][SUMMARY][DURATION]/60)
    time = ""

    if (res_hr:=int(res_mn/60)) >= 1:
        time = str(res_hr) + " h " + f"{res_mn%60:02d}" + " mn"
    else:
        time = f"{res_mn:02d}" + " mn"

    if depart.name == "":
        return " …… " + time + " …… " + arriv.name
    
    if arriv.name == "":
        return depart.name + " …… " + time + " …… "

    return depart.name + " …… " + time + " …… " + arriv.name


# TEMPS DE TRAJET
# Estimation du temps de trajet voiture entre deux points géographiques SANS format.
def time_between(depart: ReportStep, arriv: ReportStep) -> str:
    ROUTES = 'routes'
    SUMMARY = 'summary'
    DURATION = 'duration'

    ORS_KEY = '5b3ce3597851110001cf62488dbf498826f54bbb859dd1aa67054989'
    client = openrouteservice.Client(key=ORS_KEY) 

    route=client.directions(coordinates=[depart.coord, arriv.coord],
                            profile='driving-car')
    
    res_mn = int(route[ROUTES][0][SUMMARY][DURATION]/60)
    time = ""

    if (res_hr:=int(res_mn/60)) >= 1:
        time = str(res_hr) + " h " + f"{res_mn%60:02d}" + " mn"
    else:
        time = f"{res_mn:02d}" + " mn"

    return time


# CRÉATION DE ROUTE
# Ajout des coordonnées du 'poi' avec son nom.
@router.post("/poi_add")
def add_step(coordinates: Coord) -> None:
    global routes, steps

    lat_long = [coordinates.lat, coordinates.long]
    long_lat = [coordinates.long, coordinates.lat]

    res_name = requests.get("http://data:5000/poi_file_path", timeout=1800)
    json_file_name = str(res_name.json())

    js_file_path = "http://data:5000/poi_json_file?file_path=" + json_file_name
    res = requests.get(js_file_path,timeout=1800)
    df = pd.DataFrame(res.json())

    name: str = df.loc[coordinates.id,'nom']
    
    poi_coord_steps = ReportStep(name, lat_long)
    if poi_coord_steps not in steps: steps.append(poi_coord_steps)

    poi_coord_routes = ReportStep(name, long_lat)
    if poi_coord_routes not in routes: routes.append(poi_coord_routes)

    return routes, steps


# CRÉATION DE ROUTE
# Suppression des coordonnées du 'poi' et de son nom.
@router.post("/poi_remove")
def remove_step(coordinates: Coord) -> None:
    global routes, steps

    lat_long = [coordinates.lat, coordinates.long]
    long_lat = [coordinates.long, coordinates.lat]

    res_name = requests.get("http://data:5000/poi_file_path", timeout=1800)
    json_file_name = str(res_name.json())

    js_file_path = "http://data:5000/poi_json_file?file_path=" + json_file_name
    res = requests.get(js_file_path,timeout=1800)
    df = pd.DataFrame(res.json())

    name: str = df.loc[coordinates.id,'nom']

    poi_coord_steps = ReportStep(name, lat_long)
    for poi_s in steps:
        if (poi_s.name == poi_coord_steps.name) and\
            (poi_s.coord[0] == poi_coord_steps.coord[0]) and\
                (poi_s.coord[1] == poi_coord_steps.coord[1]):
            del steps[steps.index(poi_s)]   

    poi_coord_routes = ReportStep(name, long_lat)
    for poi_r in routes:
        if (poi_r.name == poi_coord_routes.name) and\
            (poi_r.coord[0] == poi_coord_routes.coord[0]) and\
                (poi_r.coord[1] == poi_coord_routes.coord[1]):
            del routes[routes.index(poi_r)]

    return routes, steps

# CRÉATION DE ROUTE
# Vérification des adresses de départ et d'arrivée avant toute création de route
# pour adapter la liste de toutes les étapes géographiques de l'utilisateur.
def check_before_create() -> None:
    global steps, routes
    global is_departure, is_arrival
    global departure, arrival

    addr_resp = requests.get('http://server:5000/get_address',
                             timeout=1800)
    addr = addr_resp.json()

    if addr[HTML_ADDR_DEP_ID] != "":
        is_departure = True
        departure = addr_to_coord(addr[HTML_ADDR_DEP_ID])

    if addr[HTML_ADDR_ARR_ID] != "":
        is_arrival = True
        arrival = addr_to_coord(addr[HTML_ADDR_ARR_ID])

    if is_departure is False: return

    # Pas d'adresse d'arrivée mentionnée.
    # On met l'adresse de départ en premier et en dernier
    # pour faire une boucle.
    if len(steps) != 0:
        steps.insert(0, departure)
        routes.insert(0,ReportStep(departure.name,[departure.coord[1], departure.coord[0]]))
    else:
        steps.append(departure)
        routes.append(ReportStep(departure.name,[departure.coord[1], departure.coord[0]]))
        
    if is_arrival is False:
        steps.append(departure)
        routes.append(ReportStep(departure.name,[departure.coord[1], departure.coord[0]]))

        return

    # On ajoute l'adresse d'arrivée en dernier.
    steps.append(arrival)
    routes.append(ReportStep(arrival.name, [arrival.coord[1],arrival.coord[0]]))

 
# CRÉATION D'UNE ROUTE
# Utilisation de la liste des 'poi' créée et mise à jour de l'interface graphique pour l'estimation du temps de trajet.
@router.post("/create_route")
def create_route():# -> bool | FileResponse:
    global routes, steps
    check_before_create()

    if  len(routes) <= 1: return False

    rootes = remove_name_from(routes) #Suppression du nom pour ne laisser que les coordonnées pour 'openrouteservice'.

    #Tracé du trajet le plus court qui passe pas tous les 'poi'.
    ORS_KEY = '5b3ce3597851110001cf62488dbf498826f54bbb859dd1aa67054989'
    client = openrouteservice.Client(key=ORS_KEY)
    route = client.directions(coordinates=rootes, profile='driving-car')
    decode = convert.decode_polyline(route['routes'][0]['geometry'])

    mini_steps = [[lat, lon] for lon, lat in decode['coordinates']]

    html = None

    with open(ROUTE_FILE_PATH, 'r') as mapfile:
        html = mapfile.read()

    map_name = find_map_variable_name(html)
    start_index = find_start_index(html)

    # Injection du code pour la visualisation de la route à la fin du fichier HTML.
    with open(ROUTE_FILE_PATH, 'w') as mapfile:
        mapfile.write(
            html[:start_index] + \
                html_code(mini_steps, map_name)
        )

    res_mn: int = int(route['routes'][0]['summary']['duration']/60)
    time: str = ""

    if (res_hr:=int(res_mn/60)) >= 1:
        time = str(res_hr) + " h " + f"{res_mn%60:02d}" + " mn"
    else:
        time = f"{res_mn:02d}" + " mn"

    time_estimation(time) # Bilan et affichage de l'estimation du temps de trajet

    return FileResponse(ROUTE_FILE_PATH,
                        media_type='text/html')


# CONVERSION ADRESSE -> (ADRESSE, [LAT, LONG])
def addr_to_coord(addr: str) -> ReportStep:

    location = ArcGIS().geocode(addr)
    addr_lat = str(location.latitude)
    addr_long = str(location.longitude)

    return ReportStep(addr, [addr_lat, addr_long])


# CRÉATION FICHIER 'ROUTES' POUR OPENROUTESERVICE
def remove_name_from(rootes:list[ReportStep]) -> tuple[str, str]:
    final_routes: tuple[str, str]

    final_routes = [[rootes[0].coord[0], rootes[0].coord[1]]]

    for route in rootes[1:]:
        final_routes.append([route.coord[0], route.coord[1]])

    return final_routes


# CRÉATION FICHIER NOM DES 'ROUTES' POUR AFFICHAGE
def get_name_from(rootes:list[ReportStep]) -> list[str]:
    # names: list[str] = [route.name for route in rootes]

    return [route.name for route in rootes]


# REMISE À ZÉRO DES ROUTES
@router.post("/clean_routes")
def clean_routes() -> None:
    global departure, arrival, routes, steps

    departure = ("","")
    arrival = ("","")
    routes.clear()
    steps.clear()


# TEMPS DE TRAJET
# Estimation du temps de trajet entre chaque point géographique défini par l'utilisateur.
def estimate_travel_time_user(geo_points:list[str], total_time: str ) -> str:
    global departure, arrival

    is_depart: bool= False
    is_arriv: bool= False
    estimated_time_user: str = ""

    addr_resp = requests.get('http://server:5000/get_address',
                             timeout=1800)
    addr = addr_resp.json()

    if addr[HTML_ADDR_DEP_ID] != "":
        is_depart = True
        departure = addr_to_coord(addr[HTML_ADDR_DEP_ID])

    if addr[HTML_ADDR_ARR_ID] != "":
        is_arriv = True
        arrival = addr_to_coord(addr[HTML_ADDR_ARR_ID])

    nb_user_points = len(geo_points)

    if (nb_user_points == 0):
        if (is_depart is True) and (is_arriv is True):
            return calculate_time(ReportStep(DEPARTURE_REPORT, [departure.coord[1], departure.coord[0]]),
                                  ReportStep(ARRIVAL_REPORT, [arrival.coord[1], arrival.coord[0]]))
        return ""

    estimated_time_user = calculate_time(ReportStep(DEPARTURE_REPORT, (departure.coord[1], departure.coord[0])),
                                         ReportStep("ÉTAPE_1", (user_points[0][1], user_points[0][0])))
    
    if nb_user_points != 1:
        for up in user_points[1:]:
            ind: int = int(user_points.index(up))
            estimated_time_user += calculate_time(ReportStep("", (user_points[ind-1][1], user_points[ind-1][0])),
                                                  ReportStep("ÉTAPE_" + str(ind + 1), (up[1], up[0])))

    estimated_time_user += calculate_time(ReportStep("", (user_points[nb_user_points-1][1], user_points[nb_user_points-1][0])),
                                          ReportStep(ARRIVAL_REPORT, (arrival.coord[1], arrival.coord[0])))
    
    estimated_time_user = "TOTAL : " + total_time + "  ----->  " + estimated_time_user
    return estimated_time_user

    # global is_departure, is_arrival, routes
    # estimated_time: str = ""

    # if len(routes) < 2: return estimated_time
    
    # if len(routes) == 2:
    #     return calculate_time(ReportStep(DEPARTURE_REPORT, routes[0]),
    #                           ReportStep(ARRIVAL_REPORT, routes[1]))
    # if len(routes) == 3:
    #     estimated_time += calculate_time(ReportStep(DEPARTURE_REPORT, routes[0]),
    #                                      ReportStep(STEP_REPORT + str(1), routes[1]))
    #     estimated_time += calculate_time(ReportStep("", routes[1]),
    #                                      ReportStep(ARRIVAL_REPORT, routes[2]))
    # else:
    #     estimated_time += calculate_time(ReportStep(DEPARTURE_REPORT, routes[0]),
    #                                      ReportStep("", routes[1]))
    #     for step in range(1,len(routes)-2):
    #         estimated_time += calculate_time(ReportStep(STEP_REPORT + str(step), routes[step]),
    #                                          ReportStep("", routes[step+1]))
    #     estimated_time += calculate_time(ReportStep(STEP_REPORT + str(step+1), routes[step+1]),
    #                                      ReportStep(ARRIVAL_REPORT, routes[step+2]))

    # return estimated_time


# TEMPS DE TRAJET
# Estimation du temps de trajet entre chaque 'poi'.
def estimate_travel_time_poi(rootes: list[ReportStep]) -> str:
    rootes_len: int = len(rootes)
    poi_path: str = '''
'''
    poi_names = get_name_from(rootes)

    if rootes_len == 2:
        return f"De : {poi_names[0]}\nVers : {poi_names[1]}\nDurée : {time_between(rootes[0], rootes[1])}\n"

    #Initialisation pour 'rootes_len' > 2.
    poi_path += f"Départ : {poi_names[0]}\nVers : {poi_names[1]}\nDurée : {time_between(rootes[0], rootes[1])}\n"

    if rootes_len == 3:
        poi_path += f"\nDe : {poi_names[1]}\nArrivée : {poi_names[2]}\nDurée : {time_between(rootes[1], rootes[2])}\n"
        return poi_path

    for route in rootes[1:rootes_len - 2]:
            index: int = int(rootes.index(route))
            poi_path += f"\nDe : {poi_names[index]}\nVers : {poi_names[index + 1]}\nDurée : {time_between(rootes[index], rootes[index + 1])}\n"

    poi_path += f"\nDe : {poi_names[-2]}\nArrivée : {poi_names[-1]}\nDurée : {time_between(rootes[-2], rootes[-1])}\n"

    return poi_path


# MISE À JOUR DU TEMPS DE TRAJET ENTRE CHAQUE ÉTAPE
# Calculs des temps de trajet prévus entre chaque étape géographique de l'utilisateur.
def time_estimation(total_time_travel: str) -> str:
    global routes, user_points

    estimated_time_poi = estimate_travel_time_poi(routes)
    estimated_time_user = estimate_travel_time_user(user_points, total_time_travel)

    requests.post('http://server:5000/update_time_estimation/',
                  headers = {'Content-Type': 'application/json'},
                  json={'eta_user': estimated_time_user,
                        'eta_poi': estimated_time_poi},
                  timeout=1800) #Mise à jour de l'interface graphique


if __name__ == "__main__":
    test = "hello"

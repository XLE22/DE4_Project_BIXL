import os, shutil
from typing import Dict,Any
import requests
import logging
# import requests
# from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.accueil.final_time_report import change_html_content, change_text_alert

ACCUEIL_FOLDER_PATH = "/app/accueil"
HTML_ADDR_DEP_ID = "departure" #ID de l'objet contenant l'adresse de départ défini dans le fichier HTML
HTML_ADDR_ARR_ID = "arrival" #ID de l'objet contenant l'adresse d'arrivée défini dans le fichier HTML

logger=logging.getLogger('main_logger')

app = FastAPI()
app.mount("/src", StaticFiles(directory=ACCUEIL_FOLDER_PATH)) #Indication du chemin CSS dans le HTML
app.mount("/images", StaticFiles(directory=ACCUEIL_FOLDER_PATH + "/images")) #Indication du chemin des images dans le HTML

addr: Dict = {HTML_ADDR_DEP_ID:"",
              HTML_ADDR_ARR_ID:""} #Contient l'adresse de départ et l'adresse d'arrivée indiquées par l'utilisateur

themes_filter: list[str]=["Commerce", 
                          "Culture",
                          "Événement",
                          "Hébergement",
                          "Loisirs",
                          "Patrimoine",
                          "Restauration",
                          "Service",
                          "Site naturel"] #Filtres choisis par l'utilisateur dans l'interface graphique
search_radius: int = 5000 #Rayon de recherche de 'poi' par défaut autour des étapes souhaitées par l'utilisateur.
time_estimation: str = "" #Affichage du temps prévu entre chaque étape pour le trajet en voiture.


# MISE À JOUR DU TEMPS ENTRE CHAQUE ÉTAPE
# Il suffit de donner la chaîne à afficher en entrée et de recharger le fichier 'html'.
@app.post("/update_time_estimation/")
def update_time_estimation(text_content: Dict) -> None:
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    HTML_FILE_PATH = FILE_PATH + '/accueil/accueil.html'

    change_html_content(HTML_FILE_PATH,
                        "travel_time_estimation",
                        text_content['eta_user'])
    
    change_text_alert(HTML_FILE_PATH,
                      text_content['eta_poi'])


# CHARGEMENT DE LA PAGE D'ACCUEIL
@app.get("/")
def display_accueil() -> FileResponse:
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    HTML_FILE_PATH = FILE_PATH + '/accueil/accueil.html'
    return FileResponse(HTML_FILE_PATH)


# RÉCUPÉRATION DES ADRESSES ISSUES DE L'INTERFACE GRAPHIQUE
@app.post("/send_address")
def send_address(addr_from_user: list[Any] = None) -> None:

    if HTML_ADDR_DEP_ID in addr_from_user[0]:
        addr[HTML_ADDR_DEP_ID] = ""
        if len(addr_from_user[0][HTML_ADDR_DEP_ID]) != 0:
            addr[HTML_ADDR_DEP_ID] = addr_from_user[0][HTML_ADDR_DEP_ID]
            
    if HTML_ADDR_ARR_ID in addr_from_user[0]:
        addr[HTML_ADDR_ARR_ID] = ""
        if len(addr_from_user[0][HTML_ADDR_ARR_ID]) != 0:
            addr[HTML_ADDR_ARR_ID] = addr_from_user[0][HTML_ADDR_ARR_ID]


# MISE À DISPOSITION DES ADRESSES RÉCUPÉRÉES DE L'INTERFACE GRAPHIQUE
@app.get("/get_address")
def get_address() -> Dict:
    global addr
    return addr


# RÉCUPÉRATION DES THÈMES
@app.post("/user_themes")
def user_themes(themes: list[Any] = None):
    global themes_filter
    
    themes_filter = []
    themes_filter = [elt['label'] for elt in themes]

    # return themes_filter


# MISE À DISPOSITION DES THÈMES
@app.get("/get_user_themes")
def get_user_themes() -> list[str]:
    global themes_filter
    
    return themes_filter


# RÉCUPÉRATION DU RAYON DE RECHERCHE
@app.post("/search_field")
def search_field(radius: list[Any] = None) -> None:
    global search_radius
    if "radius" in radius[0]: search_radius = int(radius[0]["radius"])*1000


# MISE À DISPOSITION DU RAYON DE RECHERCHE
@app.get("/get_search_field")
def get_search_field() -> int:
    global search_radius
    
    return search_radius


# ACTIVATION DU BOUTON PROPOSITION
# Spécifications dans les scripts du fichier 'accueil.html'.
@app.post("/poi_suggestions")
def poi_suggestions():# -> bool:
    requests.put('http://map:5000/tweak_poi_suggestion', timeout=1800)
    pois = requests.get('http://map:5000/map_search/get_nearest_poi', timeout=1800)
    return pois.json()
 

# ACTIVATION DU BOUTON VALIDATION
# Spécifications dans les scripts du fichier 'accueil.html'.
@app.post("/poi_validation")
def poi_validation() -> None:
    # als = 
    requests.post('http://map:5000/map_create/create_route', timeout=1800)
    # return als.json()


# # REMISE PAR DÉFAUT DES VALEURS... UN PEU PARTOUT
@app.post("/clean_html")
def clean_html() -> None:
    global addr, themes_filter, search_radius, time_estimation

    requests.post('http://map:5000/map_create/clean_routes',
                  timeout=1800) #Variable 'routes'

    requests.post('http://map:5000/clean_route',
                  timeout=1800) #Ensemble des 'polyline' dans le fichier HTML
    
    addr =  {HTML_ADDR_DEP_ID:"",
              HTML_ADDR_ARR_ID:""}
    themes_filter=["Commerce",
                   "Culture",
                   "Événement",
                   "Hébergement",
                   "Loisirs",
                   "Patrimoine",
                   "Restauration",
                   "Service",
                   "Site naturel"]
    search_radius = 5000
    time_estimation = ""
    elt={'eta_user': "",
         'eta_poi': ""}
    update_time_estimation(elt) #Estimation de temps de trajet sur l'interface graphique
    
    requests.post('http://map:5000/map_create_marker/clean_user_points',
                  timeout=1800) #Points géographiques de l'utilisateur

    requests.post('http://map:5000/clean_html_poi_suggestions',
                  timeout=1800) #Fichier HTML des 'poi' vidé
    
    requests.put('http://map:5000/tweak_first_launch',
                  timeout=1800) #Paramètre 'is_first_launch' mis à True

    #is_departure is_arrival et les departure et arrival à remettre à zéro dans create.py.

if __name__ == "__main__":
    # load_dotenv() #Charge les variables d'environnement présentes dans '.env'.
    # get_log_from(LogLevels.debug)
    hel="hello"

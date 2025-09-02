import os
import requests

import folium
from folium.plugins import MarkerCluster

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd

from .route.create import router as map_create_router
from .route.create_marker import router as map_create_marker_router
from .route.search_poi import router as map_search_router
from .route.create_marker import insert_html_code_for_marker
from .route.create_circle import create_circle_from, insert_html_code_for_circle
from .route.search_poi import get_nearest_poi

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_FILE_PATH = os.path.dirname((FILE_PATH))
FOLIUM_FILE_PATH = PARENT_FILE_PATH + '/map/files/folium-map.html'
FOLIUM_POI_SUGGESTION_FILE_PATH = PARENT_FILE_PATH + '/map/files/folium-poi-suggestion-map.html'

is_first_launch: bool=True
is_poi_suggestion: bool=False

app = FastAPI()
app.include_router(map_create_router)
app.include_router(map_create_marker_router)
app.include_router(map_search_router)

# CORS = propriété de fetch() pour le code html
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


# Existence du fichier 'json'.
def get_json_file() -> str:

    res_name = requests.get("http://data:5000/poi_file_path", timeout=1800)
    res_str = str(res_name.json())
    
    if res_str.rsplit('.',1)[1] == "json": return res_str
    
    return ""
    
    
# Affichage simplifié en HTML pour l'adresse.
def html_address(block) -> str:
    addr:str = ""
    adr_prefix:str = ""

    for elt in block:
        if type(elt) is not list:
            addr += adr_prefix + str(elt)
            adr_prefix = ", "
        else:
            for j in elt:
                addr += adr_prefix + str(j)
                adr_prefix = ", "
            adr_prefix = " - "

    return addr


# Affichage simplifié en HTML pour les contacts.
def html_contact(block) -> str:
    contact:str=""
    cont_prefix:str=""

    for cont in block:
        if type(cont) is not list:
            contact += cont_prefix + str(cont)
            cont_prefix = " - "

    return contact


def clean_folium_file() -> bool:
    global FOLIUM_FILE_PATH

    if os.path.exists(FOLIUM_FILE_PATH): # Efface le contenu du fichier
        with open(FOLIUM_FILE_PATH, 'w') as f:
            f.write("")
            return True
        
    return False


def create_first_html():
    global is_poi_suggestion

    folium_map=folium.Map(location=(48.18907660629183, -2.8428115090432),
                          control_scale=True,
                          zoom_start=8)
    marker_cluster = MarkerCluster().add_to(folium_map)
    folium.LatLngPopup().add_to(folium_map) #Utilisé pour la création des zones proposées par l'utilisateur.

    json_file_name: str = get_json_file()
    
    js_file_path = "http://data:5000/poi_json_file?file_path=" + json_file_name
    res = requests.get(js_file_path,timeout=1800)
    df = pd.DataFrame(res.json())

    for i in range(0, len(df)):

        stars= "⭐️" * df.iloc[i]['etoiles']  # Affichage simplifié en HTML pour les avis
        adr=html_address(df.iloc[i]['adresse'])
        contact=html_contact(df.iloc[i]['contact'])

        df_series = df['nom']
        elt_id = list(df_series).index(df.iloc[i]['nom'])

        html=f"""
                <h1>%s %s</h1>
                <p>%s</p>
                <h2"><strong>Adresse : </strong></h2>
                <p">%s</p>
                <h2"><strong>Contact : </strong></h2>
                <p">%s</p>
                <br/>
                <button onClick='
                    fetch("http://localhost:5003/map_create/poi_add",{{
                        method: "POST",
                        headers: {{
                            "Accept": "application/json",
                            "content-type": "application/json"
                        }},
                        body: JSON.stringify({{
                            "id": %f,
                            "lat": %f,
                            "long": %f
                        }})
                    }});
                '> Ajouter </button>
                <button onClick='
                    fetch("http://localhost:5003/map_create/poi_remove",{{
                        method: "POST",
                        headers: {{
                            "Accept": "application/json",
                            "content-type": "application/json"
                        }},
                        body: JSON.stringify({{
                            "id": %f,
                            "lat": %f,
                            "long": %f
                        }})
                    }});
                '> Supprimer </button>
                """ % (df.iloc[i]['nom'],
                       stars,
                       df.iloc[i]['description'],
                       adr,
                       contact,
                       elt_id,
                       float(df.iloc[i]['geoloc'][0]),
                       float(df.iloc[i]['geoloc'][1]),
                       elt_id,
                       float(df.iloc[i]['geoloc'][0]),
                       float(df.iloc[i]['geoloc'][1]))
        
        iframe = folium.IFrame(html=html,
                               width=400,
                               height=200)
        
        popup = folium.Popup(iframe,
                             max_width=1000)

        folium.Marker(location=[float(df.iloc[i]['geoloc'][0]),
                                float(df.iloc[i]['geoloc'][1])],
                    popup=popup,
                    tooltip=df.iloc[i]['themes'],
                    icon=folium.Icon(color="darkblue", icon="info-sign"),
                    lazy=True
                    ).add_to(marker_cluster)

    folium_map_file_path: str = FOLIUM_FILE_PATH

    # Création de cerles autour des lieux géographiques de l'utilisateur.
    if is_poi_suggestion is True:
        folium_map_file_path = FOLIUM_POI_SUGGESTION_FILE_PATH
        is_poi_suggestion = False

        if len(pois:=get_nearest_poi()) > 0:
            create_circle_from(pois,folium_map)

    folium_map.save(folium_map_file_path)

    # Injection de code pour la création de markers (étapes souhaitées par l'utilisateur).
    insert_html_code_for_marker(folium_map_file_path)

    # Injection de code pour la suppression des cercles autour des propositions de 'poi'.
    insert_html_code_for_circle(folium_map_file_path)

    # # map_html = folium_map.get_root().render()
    # # return map_html
    return FileResponse(folium_map_file_path,
                        media_type='text/html')


# CHARGEMENT DU FICHIER HTML POUR FOLIUM
# Au premier lancement, on charge la base de données uniquement.
# Pour les autres chargements, on prend en compte les modifications apportées.
@app.get("/",response_class=HTMLResponse)
def main() -> str:
    global is_first_launch

    if is_first_launch or is_poi_suggestion:
        if is_first_launch: clean_folium_file()
        is_first_launch=False
        return create_first_html()
    
    return FileResponse(FOLIUM_FILE_PATH,
                        media_type='text/html')


# SUPPRESSION DE ROUTES DANS LE FICHIER HTML
# Efface la partie de code concernant la création de routes.
@app.post("/clean_route")
def clean_route():

    with open(FOLIUM_FILE_PATH, 'r') as mapfile:
        html_file = mapfile.read()

    pattern = "var poly_line"

    starting_index = html_file.find(pattern)

    with open(FOLIUM_FILE_PATH, 'w') as mapfile:
        mapfile.write(
            html_file[:starting_index] + \
                '''
</script>
</html>'''
        )


# VIDAGE DU FICHIER HTML DES SUGGESTIONS POI
# Efface tout le code présent dans ce fichier.
@app.post("/clean_html_poi_suggestions")
def clean_html_poi_suggestions() -> bool:
    global FOLIUM_POI_SUGGESTION_FILE_PATH

    if os.path.exists(FOLIUM_POI_SUGGESTION_FILE_PATH): # Efface le contenu du fichier
        with open(FOLIUM_POI_SUGGESTION_FILE_PATH, 'w') as f:
            f.write("")
            return True
        
    return False


# Modification des paramètres indiquant un clic sur le bouton PROPOSITION
# pour adapter le fichier HTML à charger dans 'main()' et 'create_first_html()'.
@app.put("/tweak_poi_suggestion")
def tweak_poi_suggestion() -> bool:
    global is_poi_suggestion

    is_poi_suggestion = True
    return True


# Remise à zéro suite au 'clean' de la bannière.
# Indication de premier lancement d'application.
@app.put("/tweak_first_launch")
def tweak_first_launch() -> bool:
    global is_first_launch

    is_first_launch = True
    return True


if __name__ == "__main__":
    # load_dotenv() #Charge les variables d'environnement présentes dans '.env'.
    # main()
    test="hello"

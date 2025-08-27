import folium
from folium.plugins import MarkerCluster

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os

import pandas as pd

from .route.create import router as map_create_router

FILE_PATH = os.path.dirname(os.path.abspath(__file__))
PARENT_FILE_PATH = os.path.dirname((FILE_PATH))
FOLIUM_FILE_PATH = PARENT_FILE_PATH + '/map/files/folium-map.html'

is_first_launch: bool=True

app = FastAPI()
app.include_router(map_create_router)

# CORS = propriété de fetch() pour le code html
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

class Coord(BaseModel):
    lat: float
    long: float

steps:list[Coord]=[]

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


def create_first_html():
    LANNION_CENTER=(48.18907660629183, -2.8428115090432)
    folium_map=folium.Map(location=LANNION_CENTER,
                        control_scale=True,
                        zoom_start=9)
    marker_cluster = MarkerCluster().add_to(folium_map)

    df = pd.read_json('app/map/files/tmp.json')

    for i in range(0, len(df)):

        stars= "⭐️" * df.iloc[i]['etoiles']  # Affichage simplifié en HTML pour les avis
        adr=html_address(df.iloc[i]['adresse'])
        contact=html_contact(df.iloc[i]['contact'])

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
                            "lat": %f,
                            "long": %f
                        }})
                    }});
                '> Supprimer </button>
                <button onClick='
                    fetch("http://localhost:5003/map_create/route_create",{{
                        method: "POST",
                        headers: {{
                            "Accept": "application/json",
                            "content-type": "application/json"
                        }},
                        body: "hello"
                    }});
                '> Route </button>
                """ % (df.iloc[i]['nom'],
                       stars,
                       df.iloc[i]['description'],
                       adr,
                       contact,
                       float(df.iloc[i]['geoloc'][0]),
                       float(df.iloc[i]['geoloc'][1]),
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

    folium_map.save(FOLIUM_FILE_PATH)
    # map_html = folium_map.get_root().render()
    # return map_html
    return FileResponse(FOLIUM_FILE_PATH,
                        media_type='text/html')


@app.get("/",response_class=HTMLResponse)
def main() -> str:
    global is_first_launch

    if is_first_launch:
        is_first_launch=False
        return create_first_html()
    
    return FileResponse(FOLIUM_FILE_PATH,
                        media_type='text/html')


if __name__ == "__main__":
    # load_dotenv() #Charge les variables d'environnement présentes dans '.env'.
    # main()
    test="hello"

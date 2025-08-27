import logging
# import requests
# import os
# from dotenv import load_dotenv
from fastapi import FastAPI
from app.logs.logs import *

logger=logging.getLogger('main_logger')
app = FastAPI()

# # CORS = propriété de fetch() pour le code html
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=['*'],
#     allow_credentials=True,
#     allow_methods=['*'],
#     allow_headers=['*'],
# )

# class Coord(BaseModel):
#     lat: float
#     long: float

# steps:list[Coord]=[]

# @app.get("/",response_class=HTMLResponse)
# def render_vmap():
#     LANNION_CENTER=(48.18907660629183, -2.8428115090432)
#     folium_map=folium.Map(location=LANNION_CENTER,
#                         control_scale=True,
#                         zoom_start=9)
#     marker_cluster = MarkerCluster().add_to(folium_map)

#     df = pd.read_json('app/tmp.json')

#     for i in range(0, len(df)):

#         # Affichage simplifié en HTML pour les avis.
#         stars= "⭐️" * df.iloc[i]['etoiles']

#         # Affichage simplifié en HTML pour l'adresse.
#         adr:str = ""
#         adr_prefix:str = ""
#         for elt in df.iloc[i]['adresse']:
#             if type(elt) is not list:
#                 adr += adr_prefix + str(elt)
#                 adr_prefix = ", "
#             else:
#                 for j in elt:
#                     adr += adr_prefix + str(j)
#                     adr_prefix = ", "
#                 adr_prefix = " - "

#         # Affichage simplifié en HTML pour les contacts.
#         contact:str=""
#         cont_prefix:str=""
#         for cont in df.iloc[i]['contact']:
#             if type(cont) is not list:
#                 contact += cont_prefix + str(cont)
#                 cont_prefix = " - "


#         html=f"""
#                 <h1>%s %s</h1>
#                 <p>%s</p>
#                 <h2"><strong>Adresse : </strong></h2>
#                 <p">%s</p>
#                 <h2"><strong>Contact : </strong></h2>
#                 <p">%s</p>
#                 <br/>
#                 <button onClick='
#                     fetch("http://localhost:2025/poi_add",{{
#                         method: "POST",
#                         headers: {{
#                             "Accept": "application/json",
#                             "content-type": "application/json"
#                         }},
#                         body: JSON.stringify({{
#                             "lat": %f,
#                             "long": %f
#                         }})
#                     }});
#                 '> Ajouter </button>
#                 <button onClick='
#                     fetch("http://localhost:2025/poi_remove",{{
#                         method: "POST",
#                         headers: {{
#                             "Accept": "application/json",
#                             "content-type": "application/json"
#                         }},
#                         body: JSON.stringify({{
#                             "lat": %f,
#                             "long": %f
#                         }})
#                     }});
#                 '> Supprimer </button>
#                 """ % (df.iloc[i]['nom'],
#                        stars,
#                        df.iloc[i]['description'],
#                        adr,
#                        contact,
#                        float(df.iloc[i]['geoloc'][0]),
#                        float(df.iloc[i]['geoloc'][1]),
#                        float(df.iloc[i]['geoloc'][0]),
#                        float(df.iloc[i]['geoloc'][1]))
        
#         iframe = folium.IFrame(html=html,
#                             width=400,
#                             height=200)
        
#         popup = folium.Popup(iframe,
#                             max_width=1000)

#         folium.Marker(location=[float(df.iloc[i]['geoloc'][0]),
#                                 float(df.iloc[i]['geoloc'][1])],
#                     popup=popup,
#                     tooltip=df.iloc[i]['themes'],
#                     icon=folium.Icon(color="darkblue", icon="info-sign"),
#                     ).add_to(marker_cluster)

#     folium_map.save("app/map/folium-map.html")
#     map_html = folium_map.get_root().render()
#     return map_html
    
# @app.post("/poi_add")
# def add_step(coordinates: Coord):
#     steps.append(coordinates)
#     return coordinates

# @app.post("/poi_remove")
# def remove_step(coordinates: Coord):
#     steps.append(coordinates)
#     return coordinates

if __name__ == "__main__":
    # load_dotenv() #Charge les variables d'environnement présentes dans '.env'.
    get_log_from(LogLevels.debug)

import os
import datetime
import shutil
import json
import pandas as pd
from fastapi import APIRouter
from app.logs import data_logger
from .poi_ontology_converter import POC

router = APIRouter(prefix="/data_create")

CONTACT = 'hasContact'
INFOS_JSON = 'file'
LOCATION = 'isLocatedAt'
LOCATION_ADDRESS = 'schema:address'
LOCATION_GEO = 'schema:geo'
NOM = 'label'
RIEN = "Info vide"

POI_NOM = "nom"
POI_THEMES = "themes"
POI_ADRESSE = "adresse"
POI_DESCRIPTION = "description"
POI_ETOILES = "etoiles"
POI_CONTACT = "contact"
POI_GEOLOC = "geoloc"
POI_GEOLOC_LAT = "lat"
POI_GEOLOC_LONG = "long"

def remove_duplicates(file_name: str) -> bool:
    try:
        df = pd.read_json(file_name)
        df[[POI_GEOLOC_LAT,POI_GEOLOC_LONG]] = pd.DataFrame(df[POI_GEOLOC].to_list(),
                                                            columns=[POI_GEOLOC_LAT,POI_GEOLOC_LONG])
        df.drop_duplicates(subset=[POI_NOM,
                                   POI_GEOLOC_LAT,
                                   POI_GEOLOC_LONG],
                            inplace=True)
        df.to_json(file_name,
                   orient='records',
                   indent=1,
                   force_ascii=False)
        return True
    except:
        data_logger.error()
        return False

def poi_get_name(db: pd.DataFrame, elt: int) -> str | bool:
    try:
        return db.loc[[elt],[NOM]].values[0][0]
    except:
        data_logger.error()
        return False
    
def poi_get_themes(j_content: str) -> list[str]:
    themes: list[str]=[]

    if '@type' not in j_content:
        themes.append(RIEN)
        return themes
    
    if len(j_content['@type']) > 0:
        for theme in j_content['@type']:
            if theme.startswith("schema:"):
                if theme[7:] not in themes: themes.append(theme[7:])
            else:
                if not theme.startswith("schema:") and \
                (theme != "PlaceOfInterest") and \
                    (theme != "PointOfInterest") and \
                        (theme not in themes):
                    themes.append(theme)
    
    if len(themes) > 0:
        final_themes: list[str]=[]
        for elt in themes:
            if elt in POC:
                if POC[elt] not in final_themes: final_themes.append(POC[elt])
        return final_themes

    themes.append(RIEN)
    return themes

def poi_get_location(j_content: str) -> list[str]:
    location_info: list[str]=[]

    if (LOCATION not in j_content) or (LOCATION_ADDRESS not in j_content[LOCATION][0].keys()):
        location_info.append(RIEN)
        return location_info
    
    if 'schema:streetAddress' in j_content[LOCATION][0][LOCATION_ADDRESS][0].keys():
        location_info.append(j_content[LOCATION][0][LOCATION_ADDRESS][0]['schema:streetAddress'])
    
    if 'schema:addressLocality' in j_content[LOCATION][0][LOCATION_ADDRESS][0].keys():
        location_info.append(j_content[LOCATION][0][LOCATION_ADDRESS][0]['schema:addressLocality'])
    
    if 'schema:postalCode' in j_content[LOCATION][0][LOCATION_ADDRESS][0].keys():
        location_info.append(j_content[LOCATION][0][LOCATION_ADDRESS][0]['schema:postalCode'])

    return location_info

def poi_get_description(j_content: str) -> str:

    if 'hasDescription' not in j_content: return ""

    if 'dc:description' in j_content['hasDescription'][0].keys() and\
        ('fr') in j_content['hasDescription'][0]['dc:description'].keys():
        return j_content['hasDescription'][0]['dc:description']['fr'][0]
    
    return ""
    
def poi_get_stars(j_content: str) -> float:

    if 'hasReview' not in j_content: return 0

    if 'hasReviewValue' in j_content['hasReview'][0].keys() and\
        'schema:ratingValue' in j_content['hasReview'][0]['hasReviewValue'].keys():
        return j_content['hasReview'][0]['hasReviewValue']['schema:ratingValue']
    
    return 0

def poi_get_contact_info(j_content: str) -> list[str]:
    contact_info: list[str]=[]

    if CONTACT not in j_content:
        contact_info.append(RIEN)
        return contact_info
    
    if 'schema:telephone' in j_content[CONTACT][0].keys():
        contact_info.append(j_content[CONTACT][0]['schema:telephone'][0])

    if 'foaf:homepage' in j_content[CONTACT][0].keys():
        contact_info.append(j_content[CONTACT][0]['foaf:homepage'][0])

    return contact_info

def poi_get_location_info(j_content: str) -> list[str] | bool:
    location_info: list[str]=[]
    
    if (LOCATION not in j_content) or (LOCATION_GEO not in j_content[LOCATION][0].keys()):
        location_info.append(RIEN)
        return location_info
    
    if (('schema:latitude') and ('schema:longitude')) in j_content[LOCATION][0][LOCATION_GEO].keys():
        location_info.append(j_content[LOCATION][0][LOCATION_GEO]['schema:latitude'])
        location_info.append(j_content[LOCATION][0][LOCATION_GEO]['schema:longitude'])
        return location_info
    
    return False
    
def poi_get_infos() -> bool:
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    PARENT_FILE_PATH = os.path.dirname((FILE_PATH))
    POI_PATH = PARENT_FILE_PATH + '/datatourisme_poi'
    INDEX_PATH = POI_PATH + '/index.json'
    
    if os.path.exists(INDEX_PATH) is False:
        data_logger.error("Le fichier index.json n'existe pas", exc_info=True)
        return False

    try:
        db = pd.read_json(INDEX_PATH)
        nb_elts = db[NOM].count()
        poi_data = {}
        poi_data_all = []

        for elt in range(0,nb_elts):
            poi_data[POI_NOM] = poi_get_name(db,elt)
            file_name: str = db.loc[[elt],[INFOS_JSON]].values[0][0]

            with open(POI_PATH + '/objects/' + file_name, encoding = 'UTF-8') as json_file:
                json_content = json.load(json_file)
                poi_data[POI_GEOLOC] = poi_get_location_info(json_content)
                poi_data[POI_THEMES] = poi_get_themes(json_content)
                poi_data[POI_ADRESSE] = poi_get_location(json_content)
                poi_data[POI_ETOILES] = poi_get_stars(json_content)
                poi_data[POI_DESCRIPTION] = poi_get_description(json_content)
                poi_data[POI_CONTACT] = poi_get_contact_info(json_content)

            poi_data_all.append(poi_data)
            poi_data = {}

        nao: datetime = datetime.datetime.now()
        file_name = f"{nao:%y%m%d}_data_poi_{nao:%H%M}.json"
        file_path = PARENT_FILE_PATH + '/' + file_name

        try:
            with open(file_path, "w", encoding = 'UTF-8') as file_tmp:
                json.dump(poi_data_all,
                          file_tmp,
                          indent=1,
                          ensure_ascii=False)

            if remove_duplicates(file_path):
                shutil.rmtree(POI_PATH, ignore_errors=True) #Suppression des sources pour limiter la taille.
                shutil.move(file_path,POI_PATH) #Déplacement du '.json' dans le répertoire approprié.
                return True
            return False
        except:
            data_logger.error()
            return False
    
    except:
        data_logger.error()
        return False
    
@router.get("/")
def main_create() -> bool:

    data_logger.info("Début de la création du fichier JSON")

    if poi_get_infos():
        data_logger.info("Création du JSON datatourisme OK")
        return True
    
    data_logger.error("⚠️ Création du JSON datatourisme NOK ⚠️")
    return False

if __name__ == "__main__":
    main_create()

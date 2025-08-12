import os
import logging
import json
from fastapi import FastAPI
import requests
from .extract.extract_from_datatourisme import router as data_extract_router
from .create.create_json_datatourisme import router as data_create_router

logger=logging.getLogger('data-main_logger')
app = FastAPI()
app.include_router(data_extract_router)
app.include_router(data_create_router)

def extract_poi_file() -> bool:
    try:
        response1 = requests.get("http://data:5000/data_extract",timeout=1800)

        if response1.status_code != 200:
            logger.error("Problème dans l'extraction des données",exc_info=True)
            return False
        return True
    except requests.exceptions.RequestException:
        logger.error("Problème dans l'extraction des données",exc_info=True)
        return False


def create_poi_json() -> bool:
    try:
        response2 = requests.get("http://data:5000/data_create",timeout=1800)

        if response2.status_code != 200:
            logger.error("Problème dans la création des données",exc_info=True)
            return False
        return True
    except requests.exceptions.RequestException:
        logger.error("Problème dans la création des données",exc_info=True)
        return False
    

@app.get("/poi_file_path")
def get_poi_file_path() -> str|bool:
    logger.info("Recherche du chemin pour atteindre le fichier POI.json")
    FILE_PATH = os.path.dirname(os.path.abspath(__file__)) # /app/data
    DATATOURISME_FOLDER = FILE_PATH + '/datatourisme_poi' # /app/data/datatourisme_poi

    if os.path.exists(DATATOURISME_FOLDER):
        files = [f for f in os.listdir(DATATOURISME_FOLDER) if len(f) >= 10 \
                                                                and f[-18:-10] == "data_poi"\
                                                                    and f[-5:] == ".json"]
        match len(files):
            case 0:
                logger.error("Le fichier POI n'existe pas",exc_info=True)
                return False
            case 1:
                return DATATOURISME_FOLDER + '/' + files[0]
            case _:
                logger.error("Il existe plus d'un fichier POI",exc_info=True)
                return False

    logger.error("Le répertoire POI n'existe pas",exc_info=True)
    return False


@app.get("/poi_json_file")
def get_poi_json_file(file_path: str):# -> str|bool:
    logger.info("Obtention du fichier POI.json")

    if get_poi_file_path() is not False:
        with open(file_path,"r", encoding = 'UTF-8') as f:
            return json.load(f)
    return False


@app.get("/")
def main() -> bool:
    logger.info("Lancement du micro service DATA")
    
    return create_poi_json() if extract_poi_file() else False


if __name__ == "__main__":
    main()

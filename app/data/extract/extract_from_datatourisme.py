import logging
import os
import io
import shutil
import zipfile
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter
# from app.logs.logs import *

logger=logging.getLogger("extract_logger")
app = FastAPI()
router = APIRouter(prefix="/data_extract")

def get_raw_data(url: str) -> requests.models.Response | bool:
    rep:requests.models.Response = requests.get(url, timeout=1000)
    if rep.status_code != 200: 
        return False
    return rep

def zip_data(data: requests.models.Response) -> zipfile.ZipFile | bool:
    try:    
        return zipfile.ZipFile(io.BytesIO(data.content))
    except Exception as e:
        logger.error("%s",e.__cause__,exc_info=True)
        return False
    
def unfold_data(data: zipfile.ZipFile) -> bool:
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    PARENT_FILE_PATH = os.path.dirname((FILE_PATH))
    DATATOURISME_FOLDER = PARENT_FILE_PATH + '/datatourisme_poi'

    if os.path.exists(DATATOURISME_FOLDER):
        logger.info("Le répertoire datatourisme existe déjà")
        try:
            shutil.rmtree(DATATOURISME_FOLDER, ignore_errors=True)
            logger.info("Suppression de l'ancien répertoire datatourisme")
        except Exception as e:
            logger.error("%s",e.__str__,exc_info=True)
            return False

    try:
        logger.info("Création du nouveau répertoire datatourisme")
        data.extractall(DATATOURISME_FOLDER)
        return True
    except Exception as e:
        print(f"ERROR : {e.__str__}")
        return False

@router.get("/")
def main_extract() -> bool:
    load_dotenv() #Charge les variables d'environnement présentes dans '.env'.
    # get_log_from(LogLevels.debug)

    logger.info("Début de l'extraction")
    
    raw_data: requests.models.Response
    zipped_data: zipfile.ZipFile
    
    if (raw_data := get_raw_data(os.getenv("URL_EXTRACTION"))) is not False:
        logger.info("URL connue et validée")
        if (zipped_data := zip_data(raw_data)) is not False:
            if unfold_data(zipped_data):
                logger.info("Répertoire datatourisme créé")
                
                return True
            
    logger.error("Problème dans l'extraction des données",exc_info=True)
    return False

if __name__ == "__main__":
    main_extract()

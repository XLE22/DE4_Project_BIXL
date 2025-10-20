import os
import io
import shutil
import zipfile
import requests
from fastapi import FastAPI, APIRouter
from app.logs import data_logger

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
        data_logger.error("%s",e.__cause__,exc_info=True)
        return False
    
def unfold_data(data: zipfile.ZipFile) -> bool:
    FILE_PATH = os.path.dirname(os.path.abspath(__file__))
    PARENT_FILE_PATH = os.path.dirname((FILE_PATH))
    DATATOURISME_FOLDER = PARENT_FILE_PATH + '/datatourisme_poi'

    if os.path.exists(DATATOURISME_FOLDER):
        data_logger.info("Le répertoire datatourisme existe déjà")
        try:
            shutil.rmtree(DATATOURISME_FOLDER, ignore_errors=True)
            data_logger.info("Suppression de l'ancien répertoire datatourisme")
        except Exception as e:
            data_logger.error("%s",e.__str__,exc_info=True)
            return False

    try:
        data_logger.info("Création du nouveau répertoire datatourisme")
        data.extractall(DATATOURISME_FOLDER)
        return True
    except Exception as e:
        print(f"ERROR : {e.__str__}")
        return False

@router.get("/")
def main_extract() -> bool:

    data_logger.info("Début de l'extraction")
    
    raw_data: requests.models.Response
    zipped_data: zipfile.ZipFile
    URL_EXTRACTION = 'https://diffuseur.datatourisme.fr/webservice/c319be5023193089b03be95f079bbfce/{c48f545b-25fe-48b3-84c7-d29f76d9e2e3}' #Bretagne
    if (raw_data := get_raw_data(URL_EXTRACTION)) is not False:
        data_logger.info("URL connue et validée")
        if (zipped_data := zip_data(raw_data)) is not False:
            if unfold_data(zipped_data):
                data_logger.info("Répertoire datatourisme créé")
                
                return True
            
    data_logger.error("Problème dans l'extraction des données",exc_info=True)
    return False

if __name__ == "__main__":
    main_extract()

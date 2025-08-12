import logging
import requests
# import os
# from dotenv import load_dotenv
from fastapi import FastAPI
from app.logs.logs import *
# from app.data.main import main

logger=logging.getLogger('main_logger')
app = FastAPI()

@app.get("/")
def get_info():
    # hop=requests.get("http://data:5000/nope",timeout=10).json()
    # return hop
    return {'non, non, noooooooooooon':'Salut les gars'}
    
if __name__ == "__main__":
    # load_dotenv() #Charge les variables d'environnement présentes dans '.env'.
    get_log_from(LogLevels.debug)
    # main()

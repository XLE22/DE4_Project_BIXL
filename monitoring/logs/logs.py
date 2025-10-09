import logging
import os
from enum import StrEnum
from dotenv import load_dotenv


class LogLevels(StrEnum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical= "CRITICAL"


def get_log_from(log_level: str = LogLevels.error) -> None:
    load_dotenv() #Charge la variable d'environnement du '.env' pour le LOG_FILE.
    
    logging.basicConfig(level=str(log_level).upper(),
                        format='%(asctime)s:%(levelname)s:%(message)s:%(funcName)s:%(lineno)d:%(name)s',
                        filename=os.getenv('LOG_FILE'))

import logging
from logging import FileHandler
from logging import Formatter

LOG_FORMAT = "%(asctime)s [%(levelname)s]: %(message)s in %(pathname)s:%(lineno)d"
LOG_LEVEL = logging.DEBUG

# app logger
APP_LOG_FILE = "./app/app.log"
app_logger = logging.getLogger("main_logger")
app_logger.setLevel(LOG_LEVEL)
app_logger_file_handler = FileHandler(APP_LOG_FILE)
app_logger_file_handler.setLevel(LOG_LEVEL)
app_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
app_logger.addHandler(app_logger_file_handler)

# data logger
DATA_LOG_FILE = "./app/data/data.log"
data_logger = logging.getLogger("data_logger")
data_logger.setLevel(LOG_LEVEL)
data_logger_file_handler = FileHandler(DATA_LOG_FILE)
data_logger_file_handler.setLevel(LOG_LEVEL)
data_logger_file_handler.setFormatter(Formatter(LOG_FORMAT))
data_logger.addHandler(data_logger_file_handler)

# map logger
MAP_LOG_FILE = "./app/map/map.log"
map_logger = logging.getLogger("map_logger")
map_logger.setLevel(LOG_LEVEL)
map_file_handler = FileHandler(MAP_LOG_FILE)
map_file_handler.setLevel(LOG_LEVEL)
map_file_handler.setFormatter(Formatter(LOG_FORMAT))
map_logger.addHandler(map_file_handler)

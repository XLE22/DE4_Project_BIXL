import os
from fastapi import APIRouter
import requests
from pydantic import BaseModel
from pyproj import CRS
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame

from app.logs import map_logger
from .create_marker import user_points


router = APIRouter(prefix="/map_search")

CENTER_LABEL = 'center'
DISTANCE_LABEL = 'distance'
GEOMETRY_LABEL = 'geometry'

CRS_MERCATOR = CRS.from_epsg(4326)#'ESPG:4326'
CRS_FRANCE = CRS.from_epsg(2154)#'ESPG:2154'

json_file_path = ""


# Existence du fichier 'json'.
def get_json_file() -> bool:
    map_logger.debug("Existence du fichier JSON")

    res_name = requests.get("http://data:5000/poi_file_path", timeout=1800)
    res_str = str(res_name.json())
    
    if res_str.rsplit('.',1)[1] == "json": return res_str
    
    return ""
    

# Création de la GeoDataFrame pour trouver les 'poi'.
def create_geodf_for(user_point_coord: list[str]) -> GeoDataFrame:
    map_logger.debug("Création de la GeoDataFrame pour trouver les POI")

    USER_POINT_LAT_CENTER = 'lat_center'
    USER_POINT_LONG_CENTER = 'long_center'

    if (json_file_name:=get_json_file()) == "": return #Pas de fichier de données 'json'
    
    js_file_path = "http://data:5000/poi_json_file?file_path=" + json_file_name
    res = requests.get(js_file_path,timeout=1800)
    df = pd.DataFrame(res.json())

    # df = pd.read_json(json_file_path)

    # Création d'une colonne spécifique au point géographique à partir de deux autres colonnes
    # générées pour cette réalisation.
    df[USER_POINT_LAT_CENTER] = user_point_coord[0]
    df[USER_POINT_LONG_CENTER] = user_point_coord[1]
    df[CENTER_LABEL] = gpd.points_from_xy(df[USER_POINT_LAT_CENTER],
                                          df[USER_POINT_LONG_CENTER],
                                          crs=CRS_MERCATOR)

    # Création de la GeoDataFrame avec une colonne spécifique issue des colonnes 'lat' et 'long'.
    gdb = gpd.GeoDataFrame(df,
                           geometry=gpd.points_from_xy(df['lat'],
                                                       df['long']),
                                                       crs=CRS_MERCATOR)

    # Coordinate Reference Systems adapté pour calculer les distances en France
    # (on passe d'un mode sphérique à un mode plan).
    gdb[GEOMETRY_LABEL] = gdb.geometry.to_crs(CRS_FRANCE)
    gdb[CENTER_LABEL] = gdb.center.to_crs(CRS_FRANCE)

    return gdb
    

# Recherche des 'poi' les plus proches du point géographique utilisateur triés par distance croissante.
def poi_inside_circle(gdf: GeoDataFrame) -> GeoDataFrame:

    search_radius = requests.get('http://server:5000/get_search_field',
                                 timeout=1800)
    radius = int(search_radius.json())
    
    inside_circle = gdf[CENTER_LABEL].buffer(radius).contains(gdf[GEOMETRY_LABEL]) # Ensemble des éléments à l'intérieur d'un cercle centré sur le poit géographique utilisateur
    gdf[DISTANCE_LABEL] = gdf[CENTER_LABEL].distance(gdf[GEOMETRY_LABEL]) # Distance entre chaque 'poi' et le point géographique utilisateur

    return gdf.loc[inside_circle == True].sort_values(DISTANCE_LABEL)


# Liste des cinq 'poi' les plus proches du point géographique utilisateur.
def filtered_poi_with_user_themes(gdf: GeoDataFrame) -> list[str]:
    map_logger.debug("Liste des cinq POI les plus proches du point géographique utilisateur")

    themes_filter = requests.get('http://server:5000/get_user_themes',
                                 timeout=1800)
    
    check_one_choice_in_themes = lambda themes: any(choice in themes for choice in themes_filter.json())
    filter_user_choices = gdf['themes'].apply(check_one_choice_in_themes)
    
    return gdf.loc[filter_user_choices][['lat', 'long']].head().values


# Recherche des cinq 'poi' les plus proches du point géographique souhaité par l'utilisateur.
@router.get("/get_nearest_poi")
def get_nearest_poi():
    map_logger.info("Recherche des cinq POI les plus proches du point géographique souhaité par l'utilisateur")

    global user_points
    
    if len(user_points) == 0: return []
    
    poi_markers: list[str] = []
    
    if get_json_file():
        for user_geo_choice in user_points:
            gdf = create_geodf_for(user_geo_choice)
            res = poi_inside_circle(gdf)
            poi_markers.append(filtered_poi_with_user_themes(res))
        return poi_markers
    return []


if __name__ == "__main__":
    test="hello"

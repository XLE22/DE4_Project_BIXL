import folium

from app.logs import map_logger


# Création des cercles autour des 'pois' proposés.
def create_circle_from(geo_sites: list[str], folium_map: folium.Map) -> None:
    map_logger.info("Création des cercles autour des POIs proposés")
    
    for geo_site in geo_sites:
        for poi in geo_site:

            poi_lat = poi[0]
            poi_long = poi[1]

            folium.Circle(location=[poi_lat, poi_long],
                          radius=25,
                          color="red",
                          weight=5,
                          fill=False,
                          ).add_to(folium_map)


# INSERTION CODE HTML
# Code à insérer pour supprimer un cercle par simple clic en évitant
# une collision de clic avec celui qui gère la création d'un marker.
def html_code() -> str:
    map_logger.info("Insertion code HTML pour suppression de cercle POI")

    return '''<script>
    document.querySelectorAll("path.leaflet-interactive").forEach(i => i.addEventListener(
    "click", function(e){
    e.stopPropagation();
    e.target.remove();
    }
    ));
</script>
</html>'''


# INSERTION CODE HTML
# Logique pour mettre du code en fin de fichier '.html'.
def insert_html_code_for_circle(html_file_path: str) -> None:
    html_folium = None

    with open(html_file_path, 'r') as mapfile:
        html_folium = mapfile.read()
    ind_start = html_folium.find("</html>")

    with open(html_file_path, 'w') as mapfile:
        mapfile.write(
            html_folium[:ind_start] + \
                html_code()
        )


if __name__ == "__main__":
    test = "hello"

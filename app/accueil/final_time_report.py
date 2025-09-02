from typing import Tuple

# RECHERCHE INDEX DANS LE FICHIER HTML
# Obtention d'un index de fin de modèle à partir d'un départ précis.
def get_index(html_file: str, index_start: int, pattern: str) -> int:
    index: int = 0
    pattern_found: bool = False

    while not pattern_found:
        if html_file[index] == pattern:
            pattern_found = True
        index += 1

    return index_start + index


# RECHERCHE INDEX DANS LE FICHIER HTML
# Obtention des index de début et de fin du texte pour un <p> avec son 'id.
def get_indices_p(html: str, elt_id: str) -> Tuple[int, int]:
    pattern: str = 'id="' + elt_id + '"'
    index: int = html.find(pattern)

    text_start: int = get_index(html[index:], index, ">")
    text_end: int = get_index(html[text_start:], text_start, "<") - 1

    return text_start, text_end


# RECHERCHE INDEX DANS LE FICHIER HTML
# Obtention des index de début et de fin du texte pour la fenêtre ALERT des temps prévisionnels de trajets.
def get_indices_a(html: str) -> Tuple[int, int]:
    pattern: str = 'let text_alert='
    index: int = html.find(pattern)

    text_start: int = get_index(html[index:], index, "`")
    text_end: int = get_index(html[text_start:], text_start, "`") - 1

    return text_start, text_end


# MISE À JOUR DU TEXTE VISIBLE POUR L'ÉVALUATION DU TEMPS DE TRAJET ENTRE LES ÉTAPES GÉOGRAPHIQUES
# Efface et remplace le texte présent sur l'interface graphique avec 'text_content'.
def change_html_content(html_file: str, elt_id: str, text_content: str) -> None:
    # Recherche des indices entre lesquels écrire le texte donné.
    with open(html_file, 'r') as f1:
        h_file = f1.read()
        ind_start, ind_end = get_indices_p(h_file, elt_id)
    del f1

    # Écriture du texte donné.
    with open(html_file, 'w') as f2:
        f2.write(h_file[:ind_start] + \
                   text_content + \
                     h_file[ind_end:])
    del f2


# MISE À JOUR DU TEXTE DANS LA FENÊTRE "ALERT" POUR L'ÉVALUATION DU TEMPS DE TRAJET ENTRE LES POI
# Efface et remplace le texte présent dans la fenêtre ALERT avec 'text_content'.
def change_text_alert(html_file: str, text_content: str):# -> None:
    # Recherche des indices entre lesquels écrire le texte donné.
    with open(html_file, 'r') as f1:
        h_file = f1.read()
        ind_start, ind_end = get_indices_a(h_file)
    del f1
    # Écriture du texte donné.
    with open(html_file, 'w') as f2:
        f2.write(h_file[:ind_start] + \
                   text_content + \
                     h_file[ind_end:])
    del f2

if __name__ == "__main__":
    hel="hello"
#     HTML_FILE="accueil.html"
#     TEXT='''
# De : Orange LANNION
# Vers : Chez moi
# Durée : 35 mn

# De : Chez moi
# Vers : Guingamp
# Durée : 1 h 05

# De : Guingamp
# Vers : Le Havre
# Durée : 2 h 35 mn
# '''
#     change_text_alert(HTML_FILE,TEXT)
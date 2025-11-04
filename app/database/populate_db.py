import json
from app import app, db, PointDInteret, Localisation, Contact
from sqlalchemy.exc import IntegrityError
from themes import theme_mapping
import os

def flatten_list(nested_list):
    """
    Aplatie une liste de listes de manière récursive.
    """
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(str(item))
    return flat_list

def populate_pois_from_json(json_file_path):
    """
    Lit un fichier JSON et importe les données dans les tables
    POI, Localisation et Contact.
    """
    
    theme_mapping = {
        "Info vide": "Événement",
        "Culturel": "Culture",
        "Gastronomie": "Loisirs",
        "Randonnée": "Activités de plein air"
    }
                                             
    if not os.path.exists(json_file_path):
        print(f"Erreur: Le fichier '{json_file_path}' n'a pas été trouvé.")
        return

    with app.app_context():
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                pois_data = json.load(f)
            
            # Assurez-vous que le JSON est une liste d'objets
            if not isinstance(pois_data, list):
                pois_data = [pois_data]

            for data in pois_data:
                try:
                    # 1. Extraction et transformation des données du JSON
                    nom = data.get('nom')
                    description = data.get('description')
                    # Le champ 'etoiles' n'est pas utilisé dans le modèle POI, on le laisse de côté
                                      
                    # Logique de catégorisation des thèmes
                    themes_list = data.get('themes', [])
                    categorized_themes = []
                    for theme in themes_list:
                        # Si le thème est dans notre dictionnaire, on utilise la catégorie
                        # Sinon, on garde le thème original
                        categorized_themes.append(theme_mapping.get(theme, theme))
                    theme = ", ".join(categorized_themes) if categorized_themes else None

                    
                    
                    
                                                     
                    
                    # Le champ s'appelle 'theme' dans le modèle POI, pas 'themes'
                    #theme = ", ".join(themes_list) if themes_list else None

                    # Données de localisation
                    geoloc = data.get('geoloc', [None, None])
                    latitude = geoloc[0]
                    longitude = geoloc[1]
                    
                    # Transformation de l'adresse en parties distinctes
                    # Correction pour extraire la ville comme une chaîne de caractères en gérant les listes imbriquées
                    adresse_json = data.get('adresse', [])
                    flattened_adresse = flatten_list(adresse_json)
                    ville = ", ".join(flattened_adresse) if flattened_adresse else None
                    
                    # Données de contact
                    contact_info_json = data.get('contact', [])
                    telephone = contact_info_json[0] if len(contact_info_json) > 0 else None
                    homepage = contact_info_json[1] if len(contact_info_json) > 1 else None

                    if not all([nom, latitude, longitude]):
                        print(f"Avertissement: Données requises (nom, lat, lon) manquantes pour une entrée. Ignoré.")
                        continue

                    # 2. Création des objets et insertion dans les tables
                    
                    # Crée les objets Localisation et Contact.
                    nouvelle_localisation = Localisation(
                        latitude=latitude,
                        longitude=longitude,
                        ville=ville,
                    )

                    nouveau_contact = Contact(
                        telephone=telephone,
                        homepage=homepage
                    )
                    
                    # Crée l'objet PointDInteret et le lie aux deux autres
                    nouveau_poi = PointDInteret(
                        nom=nom,
                        description=description,
                        theme=theme,
                        localisation=nouvelle_localisation,
                        contact=nouveau_contact
                    )
                    
                    # Ajout à la session et commit
                    db.session.add(nouveau_poi)
                    db.session.commit()
                    print(f"POI '{nom}' et ses données associées ont été importés avec succès.")

                except IntegrityError:
                    db.session.rollback()
                    print(f"Avertissement: Le POI '{nom}' semble déjà exister. Transaction annulée.")
                except Exception as e:
                    db.session.rollback()
                    print(f"Erreur inattendue pour le POI '{nom}': {e}. Transaction annulée.")

        except json.JSONDecodeError:
            print(f"Erreur: Le fichier '{json_file_path}' n'est pas un JSON valide.")

if __name__ == '__main__':
    # Remplacez 'votre_fichier.json' par le chemin de votre fichier JSON
    populate_pois_from_json('datatourisme_poi.json')
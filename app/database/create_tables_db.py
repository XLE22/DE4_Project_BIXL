# create_db.py : création des tables selon le module relationnelle de l'application 
from app import app, db # Importez 'app' et 'db' depuis votre fichier principal (app.py)
def create_database_tables():
    """
    Crée toutes les tables dans la base de données PostgreSQL
    en se basant sur les modèles SQLAlchemy définis dans app.py.
    """
    with app.app_context(): # Nécessaire pour exécuter les opérations de DB dans le contexte de l'application Flask
        db.create_all()
        print("Toutes les tables PostgreSQL ont été créées avec succès !")
      
if __name__ == '__main__':
    create_database_tables()
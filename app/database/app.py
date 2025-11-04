import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# ... (vos imports de modèles) ...

app = Flask(__name__)
# BAse de données pour l'application 
# --- Configuration de la base de données ---
# Si votre application s'exécute DANS un conteneur Docker et que la DB est aussi dans Docker (service 'db')
# Le nom d'hôte est le nom du service Docker Compose
DB_HOST = os.environ.get('DB_HOST', 'localhost') # 'db' est le nom du service dans docker-compose.yml
DB_USER = os.environ.get('POSTGRES_USER', 'voyage')
DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'secret')
DB_NAME = os.environ.get('POSTGRES_DB', 'db_bon_voyage')
DB_PORT = os.environ.get('DB_PORT', '5432') # Port interne du conteneur DB

# Utilisation de variables d'environnement pour plus de flexibilité (bonnes pratiques Docker)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Si votre application Python s'exécute HORS du conteneur Docker (sur votre machine hôte)
# et que seule la DB est dans Docker, alors l'hôte reste 'localhost' (car le port 5432 est mappé)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://monapp_user:votre_mot_de_passe_fort@localhost:5432/monapp_db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ... (le reste de vos définitions de modèles de classes) ...

# --- Définition des Modèles (Classes Python <=> Tables PostgreSQL) ---
class Contact(db.Model):
    __tablename__ = 'contacts'
    contact_id = db.Column(db.Integer, primary_key=True)
    telephone = db.Column(db.String(50), unique=True, nullable=False)
    homepage = db.Column(db.String(255))
    
    # Relation un-à-plusieurs vers la table POI
    pois = db.relationship('PointDInteret', backref='contact', lazy=True)
    
    def __repr__(self):
        return f"<Contact(id={self.contact_id}, tel='{self.telephone}')>"
   
class Localisation(db.Model):
    __tablename__ = 'localisation'
    loc_id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    ville = db.Column(db.String(100), nullable=False)
    
    # Relation un-à-plusieurs vers la table POI
    pois = db.relationship('PointDInteret', backref='localisation', lazy=True)
    
    def __repr__(self):
        return f"<Localisation(id={self.loc_id}, ville='{self.ville}')>"

class PointDInteret(db.Model):
    __tablename__ = 'points_d_interet'
    poi_id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    theme = db.Column(db.String(50))
    
    # Clés étrangères vers les tables Contact et Localisation
    contact_id = db.Column(db.Integer, db.ForeignKey('contacts.contact_id'), nullable=False)
    loc_id = db.Column(db.Integer, db.ForeignKey('localisation.loc_id'), nullable=False)

    def __repr__(self):
        return f"<PointDInteret(id={self.poi_id}, nom='{self.nom}')>"


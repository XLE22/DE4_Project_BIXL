⚠️  PRÉ-REQUIS  ⚠️
En prenant le projet tel quel, il se peut que l'accès aux données DATATOURISME ne soit plus valide. 😓
Dans ce cas, il faut créer un compte sur le site homonyme (https://diffuseur.datatourisme.fr/fr/login) et télécharger
les données au format JSON.
L'application gère tout automatiquement dès que la nouvelle clé fournie avec le compte est associée au paramètre DATATOURISME_KEY dans le code ET qu'on remplit bien les scripts présents dans la CRONTAB. 🤓

La clé d'accès à OPENROUTESERVICE est peut-être aussi obsolète. 😓
Il faut alors se créer un compte (https://openrouteservice.org) pour obtenir cette clé à rentrer dans le code où
ORS_KEY est indiqué.


📚  MODE OPÉRATOIRE  📚
Se mettre dans le répertoire où se trouve le fichier '.yml' et lancer :
=> 'docker-compose --project-name dst-de4 up -d'

1/. Avant toute chose, s'assurer qu'un fichier de données géographiques est disponible.
Pour ce faire, ouvrir un navigateur web et taper 'localhost:5001/poi_file_path' ou '127.0.0.1:5001/poi_file_path'.

2/. S'il n'y a aucune donnée géographique, lancer la collecte via un navigateur web en tapant :
=> 'localhost:5001/' ou '127.0.0.1:5001/'
Cette requête gère automatiquement le rapatriement et la création du ficheir de données géographiques.

3/. Dès que les données sont présentes, taper dans un navigateur web 'localhost:2025/' ou '127.0.0.1:2025/' pour afficher l'interface graphique.
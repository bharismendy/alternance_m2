# projet_zabbix_grafana
projet de seconde année de master informatique en alternance.
Ce projet a pour but de créer des tableaux de bord synthétique concernant l'infrastructure système du département Maine et Loire  

# Génération de pdf
### Installation des paquets nécéssaire :
    sudo apt-get update
    sudo apt-get install markdown
    sudo apt-get install htmldoc
    pip install subprocess
    pip install markdown2pdf
Exemple de commande :

    markdown <nom du fichier markdown>.md | htmldoc --cont --headfootsize 8.0 --linkcolor blue --linkstyle plain --charset utf-8 --format pdf14 - > <nom pdf>.pdf

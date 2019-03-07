#!/bin/bash

echo "suppression du dossier venv..."
rm -rf venv
echo "création de l'environement virtuel..."
virtualenv venv -p python3
echo "installation des package python..."
source venv/bin/activate
venv/bin/pip3 install -r requirement.txt 
deactivate
echo "fin de l'installation de l'environement virtuel ..."



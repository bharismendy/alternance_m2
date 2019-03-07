------------------------------
<center>Documentation de la mise en place de l'environement de travail pour le projet</center>
=======
------------------------------
Introduction
----
Ce document simple rédigé en Markdown a pour but de documenter la mise en place d'un environement de développement pour le projet de gestion automatisé des machine virtuels via les apis d'ovirt.

# Installation de python

Pour ce projet nous allons avoir besoin de python 3.0 nous allons donc l'installer :
```
sudo apt update
sudo apt -y upgrade
sudo apt install -y python3-pip
sudo apt install -y python3-venv
sudo apt install build-essential libssl-dev libffi-dev python3-dev
```

une fois python 3.0 installé nous pouvons passer à l'Installation de l'environement virtuel pour cela exécutez le script install_venv.sh à la racine du projet.

```
./install_venv.sh
```

installation des paquets pour ovirt :
```
apt-get --assume-yes install \
gcc \
libxml2-dev \
python3-dev

```
# Sources
github du sdk ovirt :
* https://github.com/oVirt/ovirt-engine-sdk/tree/master/sdk
* https://www.ovirt.org/develop/release-management/features/infra/python-sdk.html

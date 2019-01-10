--------------------------------------------------
<center>Documentation de la mise en place de Zabbix proxy</center>
=======
------------------------------
Introduction
----
Ce document simple rédigé en Markdown a pour but de documenter la mise en place du proxy Zabbix.

### Prérequis

  On met en service les dépôts epel et les utilitaires yum :

      yum install epel-release yum-utils

On met à jour le système :

      yum update

On ajoute les dépôts officiels de Zabbix :

    yum install https://repo.zabbix.com/zabbix/4.0/rhel/7/x86_64/zabbix-release-4.0-1.el7.noarch.rpm

### Installation des paquets

Installation du paquet contenant le proxy :

    yum install zabbix-proxy-pgsql postgresql-server

### Configuration de base des paquet

Initialisation de postgresql :

    systemctl enable postgresql
    postgresql-setup initdb
    systemctl start postgresql

Initialisation de zabbix proxy :

    systemctl enable zabbix-proxy
    systemctl start zabbix-proxy

### Création de la base de données

création de l'utilisateur de la base :

    su - postgres
    createuser --pwprompt zabbix

Installation de la base de données zabbix :

    createdb -O zabbix -E Unicode -T template0 zabbix
    zcat /usr/share/doc/zabbix-proxy-pgsql-4.0.0/create.sql.gz | psql -U zabbix
    zcat /usr/share/doc/zabbix-proxy-pgsql-4.0.0/schema.sql.gz | psql -U zabbix

### Configuration de zabbix proxy

Nous allons configurer le paquet zabbix proxy, pour cela éditez le fichier */etc/zabbix/zabbix_proxy.conf*
il faut éditer les paramètres suivants :

 * Server= ip ou nom dns
 * ProxyMode= 0
 * Hostname = à commenter
 * HostnameItem= system.hostname
 * DBHost= localhost
 * DBUser= zabbix
 * DBName = nom  de votre base de données
 * DBPassword= le mot de passe de l'utilisateur zabbix

dans le fichier */var/lib/pgsql/data/pg_hba.conf* veuillez a ce que le contenu soit comme ceci :

     # "local" is for Unix domain socket connections only
     local   all             all                                     md5
     # IPv4 local connections:
     host    all             all             127.0.0.1/32            md5

### définition du proxy au serveur

    Dans administration -> proxy définnissez votre proxy :
    Proxy name : hostname de votre Proxy
    Proxy mode : Active
    Proxy address : adresse ip / dns


### Sources

* https://www.zabbix.com/documentation/4.0/manual/installation/install_from_packages/rhel_centos#importing_data

* https://www.zabbix.com/documentation/4.0/manual/appendix/install/db_scripts

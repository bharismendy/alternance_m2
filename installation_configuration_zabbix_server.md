--------------------------------------------------
<center>Documentation de la mise en place de Zabbix server</center>
=======
------------------------------
Introduction
----
Ce document simple rédigé en Markdown a pour but de documenter la mise en place de Zabbix.

### Les éléments requis
| éléments  | Status      | Description |
| ----------| ----------- | ------- |
| libpcre   | Obligatoire |     PCRE library is required for Perl Compatible Regular Expression (PCRE) support. The naming may differ depending on the GNU/Linux distribution, for example 'libpcre3' or 'libpcre1'. Note that you need exactly PCRE (v8.x); PCRE2 (v10.x) library is not used.
| libevent  | Obligatoire | Required for bulk metric support and IPMI monitoring. Version 1.4 or higher. Note that for Zabbix proxy this requirement is optional; it is needed for IPMI monitoring support.
| OpenIPMI  | Optionel    |   Required for IPMI support.
| libssh2   | Optionel    |   Required for SSH support. Version 1.0 or higher.
| fping     | Optionel    |   Required for ICMP ping items.
| libcurl   | Optionel    |   Required for web monitoring, VMware monitoring and SMTP authentication. For SMTP authentication, version 7.20.0 or higher is required. Also required for Elasticsearch.
| libiksemel| Optionel    |   Required for Jabber support.
| libxml2   | Optionel    |   Required for VMware monitoring.
| net-snmp  | Optionel    |   Required for SNMP support.

### Configuration de base
la configuration utilisé pour la mise en place de cette configuration est la suivante :
* OS : CentOS
* RAM : 4096 Mo


### Prérequis

  On met en service les dépôts epel et les utilitaires yum :

      yum install epel-release yum-utils

On met à jour le système :

      yum update

On ajoute les dépôts officiels de Zabbix :

yum install https://repo.zabbix.com/zabbix/4.0/rhel/7/x86_64/zabbix-release-4.0-1.el7.noarch.rpm



### Installation des paquets

  On va donc installer le serveur Zabbix, l'agent Zabbix et aussi l'interface Web. on installe en même temps les composants essentiels à leur fonctionnement : Apache2, postgresql et PHP :

      yum install zabbix-server-pgsql zabbix-web-pgsql

### configuration de la base de données
/!\ Attention cette partie n'ai pas forcément obligatoire mais et plus de débug
On active le service et on le démarre :

    systemctl enable postgresql
    systemctl start postgresql

/!\ si le service ne démarre pas il est possible qu'il faille initialiser postgresql :

    postgresql-setup initdb

/!\ fin de la partie moyenement utile

Création de l'utilisateur "zabbix" avec entré de mot de passe, pour cela on passe sousl'utilisateur postgres puis on fait la création :

    su - postgres
    createuser --pwprompt zabbix

Avec l'utilisateur précédemment créé nous allons mettre la base de données zabbix

    su - postgres
    createdb -O zabbix -E Unicode -T template0 zabbix

on met en place le shéma :
     zcat /usr/share/doc/zabbix-server-pgsql-4.0.0/create.sql.gz  | sudo -u zabbix psql zabbix

ensuite rendez-vous dans le fichier suivant et renseignez les champs demandé :

    nano /etc/zabbix/zabbix_server.conf
    DBHost=
    DBName=zabbix
    DBUser=zabbix
    DBPassword=<username_password>

pour finir avec postgresql on le démarre et on active sont démarrage automatique :

    systemctl start zabbix-server
    systemctl enable zabbix-server

### Configuration du php pour le front end

Editez le fichier  /etc/httpd/conf.d/zabbix.conf  certains des éléments sont déjà spécifié décommenter date.timezone et changez "Rega" en "Paris" :

    php_value max_execution_time 300
    php_value memory_limit 128M
    php_value post_max_size 16M
    php_value upload_max_filesize 2M
    php_value max_input_time 300
    php_value always_populate_raw_post_data -1
    # php_value date.timezone Europe/Paris

dans le fichier */var/lib/pgsql/data/pg_hba.conf* veuillez a ce que le contenu soit comme ceci :

    # "local" is for Unix domain socket connections only
    local   all             all                                     md5
    # IPv4 local connections:
    host    all             all             127.0.0.1/32            md5

### Configuration de SELinux

on configure rapidement SELinux pour autoriser les connection au site web :

    setsebool -P httpd_can_connect_zabbix on
    setsebool -P httpd_can_network_connect_db on
    systemctl start httpd

### Configuration du front end
nous suivons le tutoriel suivant :
https://www.zabbix.com/documentation/3.0/manual/installation/install#installing_frontend

### configuration du pare-feu

nous allons ajouter 2 règle au pare-feu pour autoriser l'agent du serveur à transmettre des données :

    iptables -A INPUT -p tcp -s 127.0.0.1 --dport 10050 -m state --state NEW,ESTABLISHED -j ACCEPT
    iptables -A INPUT -p tcp -s 127.0.0.1 --dport 10051 -m state --state NEW,ESTABLISHED -j ACCEPT

### Sources

* https://www.zabbix.com/documentation/3.0/manual/installation/install_from_packages/server_installation_with_postgresql
* https://www.zabbix.com/documentation/3.0/manual/installation/install#installing_frontend
* https://www.zabbix.com/documentation/3.4/manual/installation/requirements#server

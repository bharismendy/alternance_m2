--------------------------------------------------
<center>Documentation de mise en place d'une supervision web</center>
=======
------------------------------
introduction
----

Ce document simple rédigé en Markdown à pour but de documenter la mise en place d'un serveur tomcat 8 et de sa supervision dans zabbix.

### Installation de java

Nous allons commencer par installer le serveur tomcat :

    sudo yum install java-1.7.0-openjdk-devel wget

### Création de l'utilisateur tomcat

Nous crée on l'utilisateur tomcat :

    sudo groupadd tomcat
    sudo useradd -M -s /bin/nologin -g tomcat -d /opt/tomcat tomcat

### Installation de tomcat

Nous allons maintenant installer tomcat, pour cela déplacer vous dans votre *"home"* et téléchargez le dernier binaire :

    cd ~
    wget http://apache.mirrors.ionfish.org/tomcat/tomcat-8/v8.5.34/bin/apache-tomcat-8.5.34.tar.gz

on va installer tomcat dans */opt/tomcat* :

    sudo mkdir /opt/tomcat
    sudo tar xvf apache-tomcat-8*tar.gz -C /opt/tomcat --strip-components=1

on met à jour les permissions :

    cd /opt/tomcat
    sudo chgrp -R tomcat /opt/tomcat
    sudo chmod -R g+r conf
    sudo chmod g+x conf
    sudo chown -R tomcat webapps/ work/ temp/ logs/

création du service :

    sudo vi /etc/systemd/system/tomcat.service

insérer le contenu suivant :

    # Systemd unit file for tomcat
    [Unit]
    Description=Apache Tomcat Web Application Container
    After=syslog.target network.target

    [Service]
    Type=forking

    Environment=JAVA_HOME=/usr/lib/jvm/jre
    Environment=CATALINA_PID=/opt/tomcat/temp/tomcat.pid
    Environment=CATALINA_HOME=/opt/tomcat
    Environment=CATALINA_BASE=/opt/tomcat
    Environment='CATALINA_OPTS=-Xms512M -Xmx1024M -server -XX:+UseParallelGC'
    Environment='JAVA_OPTS=-Djava.awt.headless=true -Djava.security.egd=file:/dev/./urandom'

    ExecStart=/opt/tomcat/bin/startup.sh
    ExecStop=/bin/kill -15 $MAINPID

    User=tomcat
    Group=tomcat
    UMask=0007
    RestartSec=10
    Restart=always

    [Install]
    WantedBy=multi-user.target

On redémarre le démon :

    sudo systemctl daemon-reload

pour finir on démarre tomcat, on vérifie son status et on l'ajoute au démarrage :

    sudo systemctl start tomcat
    sudo systemctl status tomcat
    sudo systemctl enable tomcat

Nous avons maintenant un serveur tomcat fonctionnel


### Mise en place de la supervision

de manière classique hors zabbix :
Nous allons commencer par configurer tomcat pour qu'il accepte d'être supervisé en lui ajouter une série d'option au démarrage :

    sudo vi /opt/tomcat/bin/setenv.sh

entrer le contenu suivant :

    CATALINA_OPTS="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=9000 -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false"

Enregistrez puis changer les permissions de l'exécutable :

    chmod 755 /opt/tomcat/bin/setenv.sh

pour vérifier que les informations on bien été modifié vous devriez voir jmx avec les commandes suivantes :

    netstat -anlp |grep 9000
    ps -ef|grep jmx

Avec zabbix :

on installe le paquet zabbix-java-gateway :

    yum install zabbix-java-gateway

Dans le fichier de configuration (vi /etc/zabbix/zabbix_java_gateway.conf) on remplace certain paramètre :

    LISTEN_IP="0.0.0.0"
    LISTEN_PORT=10052
    START_POLLERS=5
    JAVA_OPTIONS="$JAVA_OPTIONS -Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=12345
        -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false"

on est ici dans le cas d'une machine de test donc j'ai laissé jmxremote.authenticate=false et LISTEN_IP="0.0.0.0" mais en production ce sont des paramètres à restreindre.


### Configuration de Zabbix
Nous allons maintenant déclarer l'interface JMX sur le serveur concerné (attention le port est bien le 12345):

![ajout de l'interface jmx](/image/creation_interface.png)

maintenant que l'interface existe il faut ajouter un item de gestion de l'agent jmx :

![ajout de l'item jmx](/image/creation_item_jmx.png)

### Sources

* https://www.digitalocean.com/community/tutorials/how-to-install-apache-tomcat-8-on-centos-7
* https://geekflare.com/enable-jmx-tomcat-to-monitor-administer/
* https://www.zabbix.com/documentation/3.2/manual/config/items/itemtypes/jmx_monitoring
* https://www.zabbix.com/documentation/4.0/manual/concepts/java
* https://www.zabbix.com/documentation/4.0/manual/installation/install_from_packages/rhel_centos#java_gateway_installation
* https://www.zabbix.com/documentation/4.0/manual/concepts/java/from_rhel_centos
* https://www.zabbix.com/documentation/4.0/manual/appendix/config/zabbix_java

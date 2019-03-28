--------------------------------------------------
<center>Documentation de la mise en place de Grafana</center>
=======
------------------------------
Introduction
----
Ce document simple rédigé en Markdown a pour but de documenter la mise en place de grafana et son interfaçage avec zabbix.


### Installation de Grafana
  On va commencer par ajouter le dépôt pour cela on commence par le définir :

    sudo nano /etc/yum.repos.d/grafana.repo

Ensuite nous entrons le contenu suivant :

    [grafana]
    name=grafana
    baseurl=https://packagecloud.io/grafana/stable/el/7/$basearch
    repo_gpgcheck=1
    enabled=1
    gpgcheck=1
    gpgkey=https://packagecloud.io/gpg.key https://grafanarel.s3.amazonaws.com/RPM-GPG-KEY-grafana
    sslverify=1
    sslcacert=/etc/pki/tls/certs/ca-bundle.crt


Pour finir on installe le paquet grafana :

    yum install grafana

installation via un lien vers le paquet :

    sudo yum install https://dl.grafana.com/oss/release/grafana-5.4.2-1.x86_64.rpm


### Configuration de base de grafana

On commence par activer le service au démarrage et on le démarre :

    systemctl enable grafana-server
    systemctl start grafana-server

activation de l'option de rendu d'image :

    yum install fontconfig
    yum install freetype*
    yum install urw-fonts

on autorise Grafana à utiliser le port 80 :

    sudo setcap 'cap_net_bind_service=+ep' /usr/sbin/grafana-server

dans le fichier de configuration on modifie les lignes suivantes (note, le point-virgule est utilisé pour commenter un paramètre dans les fichiers .ini):

    vim /etc/grafana/grafana.ini
    http_port = 80
    domain = xbricegr2.cg49.fr

### Ajout du plugin zabbix
Si vous avez un proxy sur votre réseau vous devez renseigner le fichier suivant :

    sudo nano /etc/environement
    http_proxy="http://proxysrv:8080/"
    https_proxy="https://proxysrv:8080/"

puis on applique les variables :

    export http_proxy="http://proxysrv:8080/"
    export https_proxy="https://proxysrv:8080/"

On install le plugin :

    grafana-cli plugins install alexanderzobnin-zabbix-app

Redémarrage de grafana pour appliquer le plugin :

    systemctl restart grafana-server

Ensuite allez dans votre interface web et passez le plugin en "enable" :

<img alt="étape 1 activation" src="/image/enable_zabbix_1.png"/>
cliquer sur le bouton enable une nouvelle fois :

<img alt="étape 2 activation" src="/image/enable_zabbix_2.png"/>


allez ensuite sur "add data Source" :

<img alt="creation du watcher" src="/image/creation_watcher.png"/>

ici j'utilise un compte admin car on est sur une compte sans grand intérêt, dans les faits
 quand vous êtes en production utilisez un compte ayant uniquement les droits de lecture
### Sources

* http://docs.grafana.org/installation/rpm/
* https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-grafana-to-plot-beautiful-graphs-from-zabbix-on-centos-7
* http://docs.grafana.org/installation/configuration/
* http://www.thesysadminhimself.com/2013/08/configuring-web-proxy-on-centos.html

--------------------------------------------------
<center>Documentation de la mise en place de Grafana</center>
=======
------------------------------
introduction
----
Ce document simple rédigé en Markdown à pour but de documenter la mise en place de grafana et son interfaçage avec zabbix.


### Installation de Grafana
  on va commencer par ajouter le dépôt pour cela on commence par le définir :

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

pour finir on installe le paquet grafana :

    yum install grafana

### configuration de base de grafana

on commence par activer le service au démarrage et on le démarre :

    systemctl enable grafana-server
    systemctl enable grafana-server

activation de l'option de rendu d'image :

    yum install fontconfig
    yum install freetype*
    yum install urw-fonts

on autorise grafana à utiliser le port 80 :

    sudo setcap 'cap_net_bind_service=+ep' /usr/sbin/grafana-server

dans le fichier de configuration on modifie les lignes suivantes (note le point-virgule est utilisé pour commenter un paramètre dans les fichier .ini):

    http_port = 80
    domain = xbricegr2.cg49.fr

### Ajout du plugin zabbix


### Sources

* http://docs.grafana.org/installation/rpm/
* https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-grafana-to-plot-beautiful-graphs-from-zabbix-on-centos-7
* http://docs.grafana.org/installation/configuration/

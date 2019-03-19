------------------------------
<center>Documentation de la mise en place de ELK</center>
=======
------------------------------
Introduction
----
Ce document simple rédigé en Markdown a pour but de documenter la mise en place de la stack elk (ElasticSearch Logstash Kibana).

### Prérequis
Pour cette mise en place nous allons utiliser une distribution linux ayant les propriétés suivantes :

    RAM : 8 GO (8192 MiO)
    CPU : 4 Cores
    Disk : 20 GO
    Java : 8 (/!\ 9 non supporté)
    web : Nginx
    Pour Nginx et java8 nous allons les installer
conseil :

    utilisation de SSL/TLS

### Installation Nginx
On commence par ajouter le repository EPEL

    sudo yum install epel-release

Nous installons Nginx :

    sudo yum install nginx


/!\ si vous avez un pare-feu vous devez autoriser le http et https :

    sudo firewall-cmd --permanent --zone=public --add-service=http
    sudo firewall-cmd --permanent --zone=public --add-service=https
    sudo firewall-cmd --reload  

on finit par démarrer nginx :

    sudo systemctl start nginx

vous pouvez accéder à Nginx en accédant à cette adresse :

    http://server_domain_name_or_IP/

Pour que le serveur démarre au boot faites la commande suivante :

    sudo systemctl enable nginx

### Installation de Java 8
Pour installer la version 8 de java openJDK 8 JRE :

    sudo yum install java-1.8.0-openjdk
Pour installer Java 8 openJDK 8 JDK


    sudo yum install java-1.8.0-openjdk-devel

### Installation et configuration d'ElasticSearch

On commence par installer la clé de chiffrement publique d'elasticsearch

    sudo rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch

on ajoute ensuite le dépôt d'ElasticSearch :

    sudo vi /etc/yum.repos.d/elasticsearch.repo

ajouter le contenu suivant :

    [elasticsearch-6.x]
    name=Elasticsearch repository for 6.x packages
    baseurl=https://artifacts.elastic.co/packages/6.x/yum
    gpgcheck=1
    gpgkey=https://artifacts.elastic.co/GPG-KEY-elasticsearch
    enabled=1
    autorefresh=1
    type=rpm-md

Enfin on lance l'installation d'elasticsearch :

    sudo yum install elasticsearch

Une fois l'installation finie on configure ElasticSearch :

      sudo nano /etc/elasticsearch/elasticsearch.yml

Ici on restreint l'écoute en localhost comme ceci :

    . . .
    network.host: localhost
    . . .

on configure pour qu'il y ai un lancement au boot et on démarre ElasticSearch :

    sudo systemctl start elasticsearch
    sudo systemctl enable elasticsearch

pour tester si le serveur répond entrer la commande suivante :

    curl -X GET "localhost:9200"

vous devriez avoir un message de ce genre :

    {
      "name" : "8oSCBFJ",
      "cluster_name" : "elasticsearch",
      "cluster_uuid" : "1Nf9ZymBQaOWKpMRBfisog",
      "version" : {
        "number" : "6.5.2",
        "build_flavor" : "default",
        "build_type" : "rpm",
        "build_hash" : "9434bed",
        "build_date" : "2018-11-29T23:58:20.891072Z",
        "build_snapshot" : false,
        "lucene_version" : "7.5.0",
        "minimum_wire_compatibility_version" : "5.6.0",
        "minimum_index_compatibility_version" : "5.0.0"
      },
      "tagline" : "You Know, for Search"
    }

### installation et configuration de Kibana

on installe, démarre et ajoute au démarrage kibana avec ces trois commandes :

    sudo yum install kibana
    sudo systemctl enable kibana
    sudo systemctl start kibana

vu que kibana est configurer en écoute localhost on doit configurer un reverse proxy à l'aide de nginx pour autoriser les accès externe. La commande suivante va créer un administrateur kibana et son mot de passe et le stocker dans htpasswd.users :

    echo "kibanaadmin:`openssl passwd -apr1`" | sudo tee -a /etc/nginx/htpasswd.users

on créer les fichiers de configuration que l'on nomme par le FQDN suivi de .conf

    sudo vi /etc/nginx/conf.d/example.com.conf

Entrez la configuration suivante en remplaçant par le bon FQDN :

    server {
        listen 80;

        server_name example.com www.example.com;

        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/htpasswd.users;

        location / {
            proxy_pass http://localhost:5601;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
    }
Une fois sauvegardé regardé si vous avec des erreurs de configuration puis rédemarrer le Nginx, enfin on autorise nginx à utiliser le service proxy :

    sudo nginx -t
    sudo systemctl restart nginx
    sudo setsebool httpd_can_network_connect 1 -P

Vous pouvez maintenant acceder à kibana via cette url :

    http://your_server_ip/status

### installation et configuration de Logstash

On commence par l'installation du logiciel :

    sudo yum install logstash

Créez un fichier de configuration nommé 02-beats-input.conf :

    sudo vi /etc/logstash/conf.d/02-beats-input.conf

entrez le contenu suivant :

    input {
      beats {
        port => 5044
      }
    }

on va maintenant créer un filtre pour les logs systèmes nommé "10-syslog-filter.conf" :

    sudo vi /etc/logstash/conf.d/10-syslog-filter.conf

avec le contenu suivant :

    filter {
      if [fileset][module] == "system" {
        if [fileset][name] == "auth" {
          grok {
            match => { "message" => ["%{SYSLOGTIMESTAMP:[system][auth][timestamp]} %{SYSLOGHOST:[system][auth][hostname]} sshd(?:\[%{POSINT:[system][auth][pid]}\])?: %{DATA:[system][auth][ssh][event]} %{DATA:[system][auth][ssh][method]} for (invalid user )?%{DATA:[system][auth][user]} from %{IPORHOST:[system][auth][ssh][ip]} port %{NUMBER:[system][auth][ssh][port]} ssh2(: %{GREEDYDATA:[system][auth][ssh][signature]})?",
                      "%{SYSLOGTIMESTAMP:[system][auth][timestamp]} %{SYSLOGHOST:[system][auth][hostname]} sshd(?:\[%{POSINT:[system][auth][pid]}\])?: %{DATA:[system][auth][ssh][event]} user %{DATA:[system][auth][user]} from %{IPORHOST:[system][auth][ssh][ip]}",
                      "%{SYSLOGTIMESTAMP:[system][auth][timestamp]} %{SYSLOGHOST:[system][auth][hostname]} sshd(?:\[%{POSINT:[system][auth][pid]}\])?: Did not receive identification string from %{IPORHOST:[system][auth][ssh][dropped_ip]}",
                      "%{SYSLOGTIMESTAMP:[system][auth][timestamp]} %{SYSLOGHOST:[system][auth][hostname]} sudo(?:\[%{POSINT:[system][auth][pid]}\])?: \s*%{DATA:[system][auth][user]} :( %{DATA:[system][auth][sudo][error]} ;)? TTY=%{DATA:[system][auth][sudo][tty]} ; PWD=%{DATA:[system][auth][sudo][pwd]} ; USER=%{DATA:[system][auth][sudo][user]} ; COMMAND=%{GREEDYDATA:[system][auth][sudo][command]}",
                      "%{SYSLOGTIMESTAMP:[system][auth][timestamp]} %{SYSLOGHOST:[system][auth][hostname]} groupadd(?:\[%{POSINT:[system][auth][pid]}\])?: new group: name=%{DATA:system.auth.groupadd.name}, GID=%{NUMBER:system.auth.groupadd.gid}",
                      "%{SYSLOGTIMESTAMP:[system][auth][timestamp]} %{SYSLOGHOST:[system][auth][hostname]} useradd(?:\[%{POSINT:[system][auth][pid]}\])?: new user: name=%{DATA:[system][auth][user][add][name]}, UID=%{NUMBER:[system][auth][user][add][uid]}, GID=%{NUMBER:[system][auth][user][add][gid]}, home=%{DATA:[system][auth][user][add][home]}, shell=%{DATA:[system][auth][user][add][shell]}$",
                      "%{SYSLOGTIMESTAMP:[system][auth][timestamp]} %{SYSLOGHOST:[system][auth][hostname]} %{DATA:[system][auth][program]}(?:\[%{POSINT:[system][auth][pid]}\])?: %{GREEDYMULTILINE:[system][auth][message]}"] }
            pattern_definitions => {
              "GREEDYMULTILINE"=> "(.|\n)*"
            }
            remove_field => "message"
          }
          date {
            match => [ "[system][auth][timestamp]", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
          }
          geoip {
            source => "[system][auth][ssh][ip]"
            target => "[system][auth][ssh][geoip]"
          }
        }
        else if [fileset][name] == "syslog" {
          grok {
            match => { "message" => ["%{SYSLOGTIMESTAMP:[system][syslog][timestamp]} %{SYSLOGHOST:[system][syslog][hostname]} %{DATA:[system][syslog][program]}(?:\[%{POSINT:[system][syslog][pid]}\])?: %{GREEDYMULTILINE:[system][syslog][message]}"] }
            pattern_definitions => { "GREEDYMULTILINE" => "(.|\n)*" }
            remove_field => "message"
          }
          date {
            match => [ "[system][syslog][timestamp]", "MMM  d HH:mm:ss", "MMM dd HH:mm:ss" ]
          }
        }
      }
    }

pour finir créer un fichier de configuration nommé "30-elasticsearch-output.conf" :

    sudo vi /etc/logstash/conf.d/30-elasticsearch-output.conf

avec ce contenu :

    output {
      elasticsearch {
        hosts => ["localhost:9200"]
        manage_template => false
        index => "%{[@metadata][beat]}-%{[@metadata][version]}-%{+YYYY.MM.dd}"
      }
    }

maintenant on test nos fichiers de configuration comme ceci :

    sudo -u logstash /usr/share/logstash/bin/logstash --path.settings /etc/logstash -t

si le résultat est bon on met en place le démarrage au boot de la machine et on démarre le logiciel :

    sudo systemctl start logstash
    sudo systemctl enable logstash

### Installation et configuration de Filebeat

Filebeat permet de collecter et transférer des fichiers de logs
installons le logiciel :

    sudo yum install filebeat

on ouvre ensuite le fichier de configuration :

    sudo vi /etc/filebeat/filebeat.yml

faites les changements pour obtenir le contenu suivant :
    ...
    #output.elasticsearch:
      # Array of hosts to connect to.
      #hosts: ["localhost:9200"]
    ...

    output.logstash:
      # The Logstash hosts
      hosts: ["localhost:5044"]

Dans un premier temps on étend le module système :

    sudo filebeat modules enable system

on peut voir la liste avec la commande suivante :

    sudo filebeat modules list

on charge le template :

    sudo filebeat setup --template -E output.logstash.enabled=false -E 'output.elasticsearch.hosts=["localhost:9200"]'

chargement avec les tableaux de bords  :

    sudo filebeat setup -e -E output.logstash.enabled=false -E output.elasticsearch.hosts=['localhost:9200'] -E setup.kibana.host=localhost:5601

maintenant on lance et met en auto start filebeat :

    sudo systemctl start filebeat
    sudo systemctl enable filebeat

Pour un module comme apache il faut spécifier le chemin d'accès au logs :

    vim /etc/filebeat/modules.d/apache2.yml

sous centos il doit avoir le contenu suivant :

    - module: apache2
      # Access logs
      access:
        enabled: true

        # Set custom paths for the log files. If left empty,
        # Filebeat will choose the paths depending on your OS.
        var.paths: ["/var/log/httpd/access_log"]

      # Error logs
      error:
        enabled: true

        # Set custom paths for the log files. If left empty,
        # Filebeat will choose the paths depending on your OS.
        var.paths: ["/var/log/httpd/error_log"]


#### Correction des problèmes
avec filebeat il y a différente manière de résoudre les problèmes que vous trouverez à l'adresse suivante :
*  https://www.elastic.co/guide/en/beats/filebeat/current/enable-filebeat-debugging.html

### Installation et configuration de MetricBeat
  on commence par installer le paquet :

    yum install metricbeat

ensuite on le configure :

    vim /etc/metricbeat/metricbeat.yml

vous devez avoir ces contenu :
    #output.elasticsearch:
      # Array of hosts to connect to.
      #hosts: ["localhost:9200"]

      output.logstash:
        # The Logstash hosts
        hosts: ["localhost:5044"]

on démarre et on active au démarrage metricbeat :

    sudo systemctl start metricbeat
    sudo systemctl enable metricbeat

on charge ensuite les template dans ElasticSearch :

    metricbeat setup --template -E output.logstash.enabled=false -E 'output.elasticsearch.hosts=["localhost:9200"]'

on force ensuite ce dernier à regarder pour de nouveau document :

    curl -XDELETE 'http://localhost:9200/metricbeat-*'

on installe ensuite les tableaux de bords via ces deux commandes :

    metricbeat setup --dashboards
    metricbeat setup -e -E output.logstash.enabled=false -E output.elasticsearch.hosts=['localhost:9200'] -E output.elasticsearch.username=metricbeat_internal -E output.elasticsearch.password=YOUR_PASSWORD -E  setup.kibana.host=localhost:5601

### Installation et configuration de packet beat
installation des paquets :

    sudo yum install libpcap
    sudo yum install packetbeat

configuration des templates :

    packetbeat setup --template -E output.logstash.enabled=false -E 'output.elasticsearch.hosts=["localhost:9200"]'


mise en place des tableaux de bords :

    packetbeat setup --dashboards

set up logstash output ;

    packetbeat setup -e \
      -E output.logstash.enabled=false \
      -E output.elasticsearch.hosts=['localhost:9200'] \
      -E output.elasticsearch.username=packetbeat_internal \
      -E output.elasticsearch.password=YOUR_PASSWORD \
      -E setup.kibana.host=localhost:5601

démarrage de packetbeat :

    sudo service packetbeat start

test de l'installation :

    curl http://www.elastic.co/ > /dev/null
    curl -XGET 'http://localhost:9200/packetbeat-*/_search?pretty'

### Sources

 * nginx :  https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-centos-7
 * elk : https://www.digitalocean.com/community/tutorials/how-to-install-elasticsearch-logstash-and-kibana-elastic-stack-on-centos-7
 * java 8 : https://www.digitalocean.com/community/tutorials/how-to-install-java-on-centos-and-fedora#install-openjdk-8
 * https://www.elastic.co/guide/en/beats/filebeat/current/configuration-path.html
 * https://www.elastic.co/guide/en/beats/filebeat/master/filebeat-module-apache.html
 * https://www.elastic.co/guide/en/logstash/master/use-filebeat-modules-kafka.html
 * https://www.elastic.co/guide/en/logstash/current/config-examples.html
 * https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-module-apache2.html
 * https://www.elastic.co/guide/en/beats/filebeat/current/filebeat-configuration.html
 * https://www.elastic.co/guide/en/logstash/current/advanced-pipeline.html
 * https://www.elastic.co/guide/en/beats/metricbeat/current/configuring-howto-metricbeat.html
 * https://www.elastic.co/guide/en/beats/metricbeat/current/metricbeat-template.html

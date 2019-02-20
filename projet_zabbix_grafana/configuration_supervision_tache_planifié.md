------------------------------
<center>Documentation de la mise en place de la supervision d'un service</center>
=======
------------------------------
Introduction
----
Ce document simple rédigé en Markdown a pour but de documenter la supervision d'un service.



Nous allons récupérer le début de l'exécution via la commande suivante :



### La commande et la tâche planifié

Pour connaître le début d'un service nous utilisons la commande suivante qui nous donne le départ du processus :

    pid=$(pgrep -u root httpd) && awk '{print $22}' /proc/$pid/stat

pour connaître le nombre de minute :

    pid=$(pgrep -u root httpd) &&ps -eo pid,etimes,command | grep $pid | grep -v grep | awk '{printf("%.2f\n", $2/60)}'

Cette commande nous retourne un float, notre but étant de monitorer une tâche planifier nous allons faire redémarrer le service httpd toute les minutes :

    crontab -e

on insère ceci pour que le service redémarre toute les minutes :

    * * * * * /bin/systemctl restart httpd.service


### Création de l'item

On créé l'item :

<img alt="création de l'item pour la tâche planifié" src="/image/creation_item_tache_planifie.png"/>

la commande à entrer est la suivante :

    system.run["pid=$(pgrep -u root httpd); ps -eo pid,etimes | grep $pid | sed -e 's/'\"$pid\"'//g'"]

### Création du trigger

Voici le screen du trigger :

<img alt="création trigger tache planifier" src="/image/creation_trigger_tache_planifié.png" />

A noter que l'on indique ">=60" car on souhaite être signaler si le process a plus de 60 second.

nous avons maintenant configuré le serveur il faut configurer le client

### Configuration du client
Dans le fichier de configuration du client (*/etc/zabbix/zabbix_agentd.conf*) on décommente les lignes suivantes et on modifie les valeurs :

    LogRemoteCommands=1
    EnableRemoteCommands=1

puis on redémarre le service :

    systemctl restart zabbix-agent

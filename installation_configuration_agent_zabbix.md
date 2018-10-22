  --------------------------------------------------
<center>Documentation de la mise en place de Zabbix agent</center>
=======
------------------------------
introduction
----
Ce document simple rédigé en Markdown à pour but de documenter la mise en place de l'agent Zabbix.

### Installation de l'agent

Pour installer l'agent sur Debian/Ubuntu exécuter la commande suivante :
    sudo apt-get install zabbix-agent

### configuration de l'agent
Nous commençons par ajouter une action (Configuration -> Actions ), dans le menu défilant "Event Source" en haut à droite il faut choisir "Auto registration", puis "create action" puis renseigner comme suis :

    Name: Linux host autoregistration
    Conditions: Host metadata contains Linux
    Operations: Link to templates: Template OS Linux

Une fois installé nous allons configurer l'agent. Pour cela nous allons éditer le fichier */etc/zabbix/zabbix_agentd.conf* ;
nous allons changers les valeurs suivantes :
* HostnameItem
* Hostname
* MetadataItem  
* ServerActive
* server
* StartAgents


    Pour "ServerActive" entrer l’adresse du serveur (ip ou nom de domaine).
    Pour "HostMetadataItem" : on renseigne le type d'OS (system.uname).
    Commenter Hostname et server.
    Pour StartAgents mettez la valeur 0
    Enfin pour "HostnameItem" : system.hostname.


enfin pensez à redémarrer l'agent.

### passage via Proxy
pour le passage du client via un proxy il nous faut renseigner le paramètre server en lui indiquant l'adresse du proxy (cela servira pour les remontées passives), ensuite on décommette le paramètre ListenIP et enfin on passe le StartAgents à 1 (on ajoute un thread d'écoute visible avec la commande "ps fax").

### Sources

* https://www.zabbix.com/documentation/4.0/manual/discovery/auto_registration
* https://www.zabbix.com/documentation/3.4/manual/web_interface/frontend_sections/configuration/actions
* https://computingforgeeks.com/how-to-install-and-configure-zabbix-agent-on-ubuntu-18-04/

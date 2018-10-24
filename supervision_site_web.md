--------------------------------------------------
<center>Documentation de mise en place d'une supervision web</center>
=======
------------------------------
introduction
----
Ce document simple rédigé en Markdown à pour but de documenter la mise en place d'une supervision de site web pour cela nous allons créer un web scénarios qui sera composé de "steps" qui sont des requêtes HTTP, ces dernières seront exécuté de manière périodique par le serveur zabbix ou par le proxy de l'hôte si il est derrière ce dernier .

Depuis Zabbix 2.2 les scénarios sont rattaché aux hôtes ou template comme les items ou les triggers.

Dans tout les web scénario les informations suivantes sont collecté :
* la vitesse moyenne de téléchargement par seconde
* le nombre de "steps" échoué
* le dernier message d'erreur

Dans chaque "steps" les informations suivantes sont collectées :
* la vitesse de téléchargement par seconde
* le temps de réponse
* le code de retour

Pour finir on peut également tester la présence d'une chaîne de caractère sur la page html ou encore simuler des cliques souris ainsi que suivre un chemin sur le site web et se connecter.

### Configurer un web scénario
Aller dans Configurations puis Template, ensuite cliquer sur web dans la ligne du template. sur la page qui s'affiche cliquer sur "create web scenario"

![étapes 1 de création de l'hôte](/image/creation_scenario_1.png)

![étapes 2 de création de l'hôte](/image/creation_scenario_2.png)

Nous avons ensuite un premier formulaire à remplir :

![étapes 3 de création de l'hôte](/image/creation_scenario_3.png)

une fois le scénario remplie nous nous rendons sur l'onglet Steps puis on clique sur "add" et de nouveau on remplie un formulaire :

![étapes 4 de création de l'hôte](/image/creation_scenario_4.png)

pour finir on dispose d'un onglet authentification qui nous sera inutile dans notre cas

![étapes 5 de création de l'hôte](/image/creation_scenario_5.png)

### Sources
* https://www.zabbix.com/documentation/4.0/manual/web_monitoring

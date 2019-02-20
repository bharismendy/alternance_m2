------------------------------
<center>Documentation de la mise en place de la supervision d'un service</center>
=======
------------------------------
Introduction
----
Ce document simple rédigé en Markdown a pour but de documenter la supervision d'un service.
Nous allons ici tenter de superviser le service httpd

### Mise en place de l'item
Pour commencer nous allons commencer par créer un item qui supervisera le service :
(à noter que j'ai fait "create new item" dans le template os linux web server)


<img alt="description de l'item" src="/image/creation_item_supervision.png"/>

la clé nous permet de dire que l'on veut superviser le service et comment on le supervise. de plus ici j'utilise proc.num car je veux aussi connaître le nombre de processus pour le remonté dans grafana, si on voulait uniquement connaître l'état on aurait utilisé service.info  

### Mise en place du trigger
Maintenant que nous avons un item nous pouvons mettre en place un trigger qui ce déclenchera dès que notre service stoppera aller dans trigger de notre template puis "create trigger" puis dans expression faites comme ceci :

<img alt="create trigger from item etape 1" src="/image/creation_trigger_from_item_1.png" />

puis finissez de remplir le formulaire :

<img alt="create trigger from item etape 2" src="/image/creation_trigger_from_item_2.png" />

### Sources

* https://www.zabbix.com/documentation/2.2/manual/config/items/itemtypes/zabbix_agent
* https://www.zabbix.com/documentation/4.0/manual/config/items/item/key
* https://www.zabbix.com/documentation/4.0/manual/config/items/item
* https://www.zabbix.com/documentation/3.0/manual/config/items/itemtypes/zabbix_agent

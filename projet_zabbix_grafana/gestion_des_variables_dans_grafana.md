--------------------------------------------------
<center>Documentation de création et la configuration de variable dans Grafana</center>
=======
------------------------------
Introduction
----
Ce document simple rédigé en Markdown a pour but de documenter la mise en place de variable dans Grafana.

### Création d'une variable

Dans un premier temps ce qu'il faut savoir c'est que les variables sont propre à un dashboard dans Grafana, c'est donc tout naturellement que nous retrouvons leur configuration dans les paramètres de ces derniers.

étape 1 : ce rendre dans les paramètres

<img alt="accès aux paramètres" src="/image/crea_var_et_1.png"/>

étape 2 : allez dans la section "Variables" puis cliquer sur "+ New"

<img alt="création de la variable" src="/image/crea_var_et_2.png"/>

étape 3 : Configuration de la variable, vous trouverez ci-dessous une configuration de variable

<img alt="Configuration de la variable" src="/image/crea_var_et_3.png"/>

Sur ce panneau on retrouve plusieurs champs :

Name : le nom réel de la variable
Label : le nom affiché de la variable
type : le type de variable
hide : permet de cacher soir le Label soit le Name
Data source : la source de données auquel s'applique la variable
Query : la requête qui permet de récupérer les différentes valeurs de la variable
Regex : permet de nettoyer les valeurs récupérer par la Query
Sort : permet de trier par ordre alphabétique
Multi-value : permet la sélection de plusieurs valeurs en même temps
Include All option : permet d'ajouter l'option "all" qui permet de sélectionner toutes les valeurs possible

Une fois ces champs renseigné vous pouvez cliquer add ou update pour valider la variable.

### Utilisation de la variable

Dans le tableau de bord vous verrez maintenant votre variable :

<img alt="affichage de la variable" src="/image/var_view.png"/>

Pour l'utilisation dans une métrique il suffit de la mettre là ou vous pourriez mettre une des valeurs qu'elle contient. Exemple :

<img alt="utilisation d'une variable" src="/image/use_var.png"/>

------------------------------
<center>Documentation de la mise en place de la supervision d'une base de donnée </center>
=======
------------------------------
introduction
----
Ce document simple rédigé en Markdown a pour but de documenter la supervision d'une base de données SQL Server, PostgreSQL, Oracle ou encore MariaDB.


### Les bases PostgreSQL

Nous allons commencer par superviser une base de données PostgreSQL. Pour cela nous allons utiliser la documentation officiel de zabbix.

#### Installation

Pour utiliser odbc on installe *postgresql-odbc* :

    yum install postgresql-odbc
    yum -y install unixODBC unixODBC-devel
    yum install mysql-connector-odbc

dans le dossier */etc* on a les fichiers odbcinst.ini et odbc.ini, on configure ces deux fichiers pour le bon fonctionnement d'ODBC :

#### Configuration

Dans  odbcinst.ini :

    # Example driver definitions

    # Driver from the postgresql-odbc package
    # Setup from the unixODBC package
    [PostgreSQL]
    Description     = ODBC for PostgreSQL
    Driver          = /usr/lib/psqlodbcw.so
    Setup           = /usr/lib/libodbcpsqlS.so
    Driver64        = /usr/lib64/psqlodbcw.so
    Setup64         = /usr/lib64/libodbcpsqlS.so
    FileUsage	= 1
    Threading	= 2
    TraceFile	= /var/log/odbc.log

    # Driver from the mysql-connector-odbc package
    # Setup from the unixODBC package
    [MySQL]
    Description     = ODBC for MySQL
    Driver          = /usr/lib/libmyodbc5.so
    Setup           = /usr/lib/libodbcmyS.so
    Driver64        = /usr/lib64/libmyodbc5.so
    Setup64         = /usr/lib64/libodbcmyS.so
    FileUsage	= 1

Dans odbc.ini :

GNU nano 2.3.1                                                       Fichier : /etc/odbc.ini                                                                                                                     

    [psql]
      Description = PostgreSQL database 1
      Driver  = postgresql
      #CommLog = /tmp/sql.log
      Username = zabbix
      Password = P@ssw0rd
      # Name of Server. IP or DNS
      Servername = 127.0.0.1
      # Database name
      Database = zabbix
      # Postmaster listening port
      Port = 5432
      # Database is read only
      # Whether the datasource will allow updates.
      ReadOnly = No
      # PostgreSQL backend protocol
      # Note that when using SSL connections this setting is ignored.
      # 7.4+: Use the 7.4(V3) protocol. This is only compatible with 7.4 and higher backends.
      Protocol = 7.4+
      # Includes the OID in SQLColumns
      ShowOidColumn = No
      # Fakes a unique index on OID
      FakeOidIndex  = No
      # Row Versioning
      # Allows applications to detect whether data has been modified by other users
      # while you are attempting to update a row.
      # It also speeds the update process since every single column does not need to be specified in the where clause to update a row.
      RowVersioning = No
      # Show SystemTables
      # The driver will treat system tables as regular tables in SQLTables. This is good for Access so you can see system tables.
      ShowSystemTables = No
      # If true, the driver automatically uses declare cursor/fetch to handle SELECT statements and keeps 100 rows in a cache.
      Fetch = Yes
      # Bools as Char
      # Bools are mapped to SQL_CHAR, otherwise to SQL_BIT.
      BoolsAsChar = Yes
      # SSL mode
      #SSLmode = Yes
      # Send tobackend on connection
      ConnSettings =



On utilise la commande suivante pour vérifier la localisation des fichiers de configuration :

    odbcinst -j

Pour vérifier la connexion on utilise la commande suivante :

    isql -v psql

#### Création de l'item

![Creation de l'item de monitoring de la base de données](/image/create_item_monitor_pgsqlDB.png)

ici on compte le nombre d'hôte une solution alternative est :

    SELECT
    SUM(pg_relation_size(C.oid))
    FROM pg_class C
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
    WHERE nspname NOT IN ('pg_catalog', 'information_schema');

Cette requête nous permet de remonter la taille de la base de données.

#### voie d'exploration
* http://pg-monz.github.io/pg_monz/index-en.html#install

### Sources
* https://www.zabbix.com/documentation/4.0/manual/config/items/itemtypes/odbc_checks
* https://www.zabbix.com/documentation/4.0/manual/config/items/itemtypes/odbc_checks/unixodbc_postgresql

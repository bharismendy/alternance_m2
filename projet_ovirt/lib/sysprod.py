# -*- coding: utf-8 -*-

# Configuration particulière pour le datacenter Sysprod

#
# Configuration réseau en fonction de :
# - la zone réseau (lan-test, lan-prod, dmz-pub, dmz-test, dmz-hbgt)
# - le nom du template choisi (centos6, centos7, ...)
#
net_conf = {
    'lan-prod': {
        'subnet': {
            'ubuntu1604': '10.100.41.0/24',
            'ubuntu1804': '10.100.41.0/24',
            'centos6': '10.100.41.0/24',
            'centos7': '10.100.41.0/24',
            'windows': '10.100.42.0/24'
        },
        'gateway': '10.100.1.1',
        'netmask': '255.255.0.0',
        'nameservers': ['10.100.49.101', '10.100.49.102'],
        'search': ['cg49.fr', 'tests.cg49.fr', 'hbgt.cg49.fr']
    },
    'lan-test': {
        'subnet': {
            'ubuntu1604': '10.100.141.0/24',
            'ubuntu1804': '10.100.141.0/24',
            'centos6': '10.100.141.0/24',
            'centos7': '10.100.141.0/24',
            'windows': '10.100.142.0/24'
        },
        'gateway': '10.100.1.1',
        'netmask': '255.255.0.0',
        'nameservers': ['10.100.49.101', '10.100.49.102'],
        'search': ['cg49.fr', 'tests.cg49.fr', 'hbgt.cg49.fr']
    },
    'dmz-pub': {
        'subnet': {
            'ubuntu1604': '172.20.20.0/24',
            'ubuntu1804': '172.20.20.0/24',
            'centos6': '172.20.20.0/24',
            'centos7': '172.20.20.0/24',
            'windows': '172.20.20.0/24'
        },
        'gateway': '172.20.20.130',
        'netmask': '255.255.255.0',
        'nameservers': ['172.20.40.21', '172.20.40.22'],
        'search': ['cg49.fr', 'tests.cg49.fr', 'hbgt.cg49.fr']
    },
    'dmz-test': {
        'subnet': {
            'ubuntu1604': '172.20.50.0/24',
            'ubuntu1804': '172.20.50.0/24',
            'centos6': '172.20.50.0/24',
            'centos7': '172.20.50.0/24',
            'windows': '172.20.50.0/24'
        },
        'gateway': '172.20.50.130',
        'netmask': '255.255.255.0',
        'nameservers': ['172.20.40.21', '172.20.40.22'],
        'search': ['cg49.fr', 'tests.cg49.fr', 'hbgt.cg49.fr']
    },
    'dmz-hbgt': {
        'subnet': {
            'ubuntu1604': '172.20.60.0/24',
            'ubuntu1804': '172.20.60.0/24',
            'centos6': '172.20.60.0/24',
            'centos7': '172.20.60.0/24',
            'windows': '172.20.60.0/24'
        },
        'gateway': '172.20.60.130',
        'netmask': '255.255.255.0',
        'nameservers': ['172.20.40.21', '172.20.40.22'],
        'search': ['cg49.fr', 'tests.cg49.fr', 'hbgt.cg49.fr']
    },
    'dmz-dtm': {
        'subnet': {
            'ubuntu1604': '172.25.1.0/24',
            'ubuntu1804': '172.25.1.0/24',
            'centos6': '172.25.1.0/24',
            'centos7': '172.25.1.0/24',
            'windows': '172.25.1.0/24'
        },
        'gateway': '172.25.1.1',
        'netmask': '255.255.255.0',
        'nameservers': ['172.20.40.21', '172.20.40.22'],
        'search': ['cg49.fr', 'tests.cg49.fr', 'hbgt.cg49.fr']
    }
}


#
# Correspondance entre la zone réseau et le profile réseau du datacenter
#
vnic_mapping = {
    'lan-prod': 'SRV',
    'lan-test': 'SRV',
    'dmz-pub': 'DMZPUB',
    'dmz-test': 'DMZTEST',
    'dmz-hbgt': 'DMZHBGT',
    'dmz-dtm': 'DMZDTM'
}


#
# Choix du cluster en fonction de:
# - la zone réseau
# - le type de VM (prod, pas prod)
#
cluster = {
    ('lan-prod', True): 'Lavoisier',
    ('lan-test', False): 'Fremur',
    ('dmz-pub', True): 'DMZ-Lavoisier',
    ('dmz-test', False): 'DMZ-Fremur',
    ('dmz-hbgt', True): 'DMZ-Lavoisier',
    ('dmz-hbgt', False): 'DMZ-Fremur',
    ('dmz-dtm', True): 'DMZ-Lavoisier',
    ('dmz-dtm', False): 'DMZ-Lavoisier'
}


#
# Choix du stockage en fonction:
# - du template (centos6, centos7 ...)
# - du type (prod/pas prod)
#
storage_domain = {
    ('centos7', True): 'prod_centos',
    ('centos7', False): 'test_linux',
    ('centos6', True): 'prod_centos',
    ('centos6', False): 'test_linux',
    ('ubuntu1604', True): 'prod_divers',
    ('ubuntu1604', False): 'test_divers',
    ('ubuntu1804', True): 'prod_divers',
    ('ubuntu1804', False): 'test_divers'
}

os_code = {
    'ubuntu1604': 'ubuntu_14_04',
    'ubuntu1804': 'ubuntu_14_04',
    'centos6': 'rhel_6x64',
    'centos7': 'rhel_7x64',
}

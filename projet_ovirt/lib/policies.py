# -*- coding: utf-8 -*-

import os
import re
import sys

import lib.crypt
from importlib import import_module


class Policies:
    def __init__(self, dc_name):
        basedir = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(basedir)
        config = import_module(dc_name.lower())
        self.net_conf = config.net_conf
        self.vnic_mapping = config.vnic_mapping
        self.storage_domain = config.storage_domain
        self.cluster = config.cluster
        self.os_code = config.os_code

    def zone_exists(self, zone):
        return zone in self.net_conf.keys()

    def vm_is_prod(self, vm_name):
        if re.match(r'^[wx].*1$', vm_name):
            return True
        elif re.match(r'^[wx].*[234]$', vm_name):
            return False
        else:
            raise Exception("nom de Vm non conforme: '{}'".format(vm_name))

    def config_vm(self, name, ram_mb, cores, vmtype, zone):
        is_prod = self.vm_is_prod(name)

        if zone == 'lan' and is_prod:
            zone = 'lan-prod'
        elif zone == 'lan':
            zone = 'lan-test'
        elif not self.zone_exists(zone):
            raise Exception("Zone inconnue: '{}'".format(zone))
        elif zone == 'dmz-pub' and not is_prod:
            raise Exception('Vm de test dans DMZ-Pub')
        elif zone == 'dmz-test' and is_prod:
            raise Exception('Vm de prod dans DMZ-Test')

        return {
            'vm_name': name,
            'memory': ram_mb * 1024 * 1024,
            'cores': cores,
            'vmtype': vmtype,
            'source_vm_name': 'template_'+vmtype,
            'is_prod': is_prod,
            'dc_name': 'Sysprod',
            'domain': 'cg49.fr',
            'fqdn': name+'.cg49.fr',
            'zone': zone,
            'vnic_name': self.vnic_mapping[zone],
            'net': {
                'gateway': self.net_conf[zone]['gateway'],
                'netmask': self.net_conf[zone]['netmask'],
                'dns_servers': self.net_conf[zone]['nameservers'],
                'dns_search': self.net_conf[zone]['search']
            },
            'sd_name': self.storage_domain[(vmtype, is_prod)],
            'cluster_name': self.cluster[(zone, is_prod)],
            'subnet_cidr': self.net_conf[zone]['subnet'][vmtype],
            'os_code': self.os_code[vmtype]
        }

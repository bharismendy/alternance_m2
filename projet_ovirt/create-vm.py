#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK

import argcomplete
import argparse

from lib import crypt
from lib.config import Config
from lib.policies import Policies
from lib.vm_cloner import VMCloner
from lib.ipam_client import IpamClient
from lib.dnsmgr import DNSMgr
VERSION = 'sc-generic-2017-04-07'


class ConfigVmCloner(Config):
    def __init__(self, cfg_file=None, with_ipam=True):
        super().__init__(cfg_file)
        self.ovirt = self.config['ovirtengine']
        self.ovirt['password'] = crypt.decode(self.ovirt['password'])
        if with_ipam:
            self.ipam = self.config['ipam']
            self.ipam['password'] = crypt.decode(self.ipam['password'])
            if self.ipam['verify'].lower() in ['yes', '1', 'true']:
                self.ipam['verify'] = True
            else:
                self.ipam['verify'] = False
            self.dnsmgr = self.config['dnsmgr']


def create_vm(name, ram=1024, cores=2, vmtype='centos7', zone='lan',
              storage=None, cfg_file=None):
    # Récupère la config réseau (hors adresse IP), le nom du cluster, du
    # storage domain, du vnic profile...
    vm_infos = Policies('Sysprod').config_vm(
        name,
        ram,
        cores,
        vmtype,
        zone
    )

    cfg = ConfigVmCloner(cfg_file)

    if storage:
        vm_infos['sd_name'] = storage

    ip = False
    with VMCloner(vm_infos, **cfg.ovirt) as cloner:
        cloner.do_basic_checking()
        cloner.set_source_disks(
            cloner.collect_disks(cloner.source_vm_name, cloner.dc_name)
        )

        with IpamClient(**cfg.ipam) as ipam:
            cloner.net['ip'] = ipam.reserve_address(
                cloner.fqdn,
                cloner.subnet_cidr
            )
            ip = cloner.net['ip']

        cloner.copy_disks()
        cloner.create_vm(vm_infos)
        cloner.add_nic('nic1')
        cloner.tag_vm(['script-created', VERSION])
        cloner.attach_disks()
        cloner.cloud_init()

    if ip:
        dnsmgr = DNSMgr(**cfg['dnsmgr'])
        dnsmgr.add_record(name, ip)


def collect_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help="nom de la vm", type=str)
    parser.add_argument('--ram', help="taille de la RAM en MB", type=int,
                        default=2048)
    parser.add_argument('--cores', help="nombre de cores", type=int,
                        default=2)
    parser.add_argument(
        '--zone', help="zone réseau",
        choices=['lan', 'dmz-pub', 'dmz-test', 'dmz-hbgt', 'dmz-dtm'],
        default='lan'
    )
    parser.add_argument("--config", type=str, help="fichier de configuration")
    parser.add_argument("--storage", type=str, help="nom du stockage")
    parser.add_argument(
        '--vmtype', help="modèle de VM",
        choices=['centos6', 'centos7', 'ubuntu1604', 'ubuntu1804'],
        default='centos7'
    )

    argcomplete.autocomplete(parser)
    return parser.parse_args()


if __name__ == '__main__':
    args = collect_args()
    print(args.name)
    create_vm(
            name=args.name,
            ram=args.ram,
            cores=args.cores,
            vmtype=args.vmtype,
            zone=args.zone,
            storage=args.storage,
            cfg_file=args.config
    )

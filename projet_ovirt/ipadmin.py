#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import argparse
import argcomplete

from lib import crypt
from lib.config import Config
from lib.ipam_client import IpamClient


class MyIPAMConfig(Config):
    def __init__(self, cfg_file=None, with_ipam=True):
        super().__init__(cfg_file)
        self.ipam = self.config['ipam']
        self.ipam['password'] = crypt.decode(self.ipam['password'])
        if self.ipam['verify'].lower() in ['yes', '1', 'true']:
            self.ipam['verify'] = True
        else:
            self.ipam['verify'] = False


#   with IpamClient(**cfg.ipam) as ipam:
#       cloner.net['ip'] = ipam.reserve_address(
#           cloner.fqdn,
#           cloner.subnet_cidr
#       )

parser = argparse.ArgumentParser()
parser.add_argument('action', help="type d'opération", choices=['request', 'reserve', 'reservethis', 'release'])
parser.add_argument('--netmask', help="masque de sous réseau", type=str)
parser.add_argument('--ip', help="adresse IP", type=str)
parser.add_argument('--fqdn', help="Nom à enregistrer", type=str)
argcomplete.autocomplete(parser)

args = parser.parse_args()

cfg = MyIPAMConfig()
if args.action == 'release':
    if args.ip is not None:
        with IpamClient(**cfg.ipam) as ipam:
            ipam.release_address(args.ip)
    else:
        print('myipam.py release --ip xxx.xxx.xxx.xxx')
elif args.action == 'reserve':
    if args.netmask is not None and args.fqdn is not None:
        with IpamClient(**cfg.ipam) as ipam:
            ip = ipam.reserve_address(args.fqdn, args.netmask)
        print('adresse: ' + ip)
    else:
        print('myipam.py reserve --fqdn name.domain --netmask xxx.xxx.xxx.xxx/nn')
elif args.action == 'reservethis':
    if args.netmask is not None and args.fqdn is not None and args.ip is not None:
        with IpamClient(**cfg.ipam) as ipam:
            ip = ipam.reserve_this_address(args.fqdn, args.netmask, args.ip)
    else:
        print('myipam.py reservethis --fqdn name.domain --netmask xxx.xxx.xxx.xxx/nn --ip xxx.xxx.xxx.xxx')

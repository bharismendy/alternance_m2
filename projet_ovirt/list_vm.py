
# -*- coding: utf-8 -*-
# the purpose of this script is to list all vm in ovirt


import sys
import time
import argparse
import argcomplete

import ovirtsdk4.types as types

from lib.my_ovirt import MyOVirt


def collect_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help="nom de la vm", type=str)
    parser.add_argument('--force', help="power off/on", action='store_true')

    argcomplete.autocomplete(parser)
    return parser.parse_args()


if __name__ == '__main__':
    with MyOVirt() as ovirt:
        vms_service = ovirt.sys.vms_service()
        try:
            vm = vms_service.list()
            for v in vm:
                print(v.name)
        except():
            exit(1)


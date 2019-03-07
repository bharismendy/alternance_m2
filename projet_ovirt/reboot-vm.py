#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    args = collect_args()
    with MyOVirt() as ovirt:
        vms_service = ovirt.sys.vms_service()
        try:
            vm = vms_service.list(search=args.name)[0]
            vm_service = vms_service.vm_service(vm.id)
        except:
            print("VM not found " + args.name)
            exit(1)

        if args.force:
            vm_service.stop()
        else:
            vm_service.shutdown()

        while True:
            time.sleep(5)
            vm = vm_service.get()
            if vm.status == types.VmStatus.DOWN:
                break

        vm_service.start()

# vim: ts=4 sw=4 expandtab


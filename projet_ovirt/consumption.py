#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys

import ovirtsdk4.types as types

from my_ovirt import MyOVirt


os_type = {'?': 0}
os_family = {'other': 0, 'linux':0, 'windows':0}
status = {'down': 0, 'up': 0}
os_other = []

with MyOVirt() as ovirt:
    try:
        vms = ovirt.sys.vms_service().list(search=sys.argv[1])
    except IndexError:
        vms = ovirt.sys.vms_service().list()

for vm in vms:
    if vm.status == types.VmStatus.DOWN:
        continue

    codename = vm.os.type
    if not re.match('windows', codename):
        continue

    #print(vm.memory)
    #print(vm.memory)
    print(vm.external_host_provider)

exit

print("{} VMs: ({} up, {} down)".format(status['up'] + status['down'], status['up'], status['down']))
print('=== OS Family ================')
sorted_os_family = [(k, os_family[k]) for k in sorted(os_family, key=os_family.get, reverse=True)]
for k, v in sorted_os_family:
    if v == 0:
        continue
    print("{}\t{}".format(v, k), end='')
    if k == 'other':
        print(' : ' + ', '.join(os_other))
    else:
        print()

print('=== OS =======================')
sorted_os_type = [(k, os_type[k]) for k in sorted(os_type, key=os_type.get, reverse=True)]
for k, v in sorted_os_type:
    if v == 0:
        continue
    print("{}\t{}".format(v, k))

#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

from lib.my_ovirt import MyOVirt

with MyOVirt() as ovirt:
    for vm in ovirt.sys.vms_service().list():
        affinity = vm.placement_policy.affinity
        if affinity.value == 'pinned':
            print("pinned: " + vm.name)
        if affinity.value == 'user_migratable':
            print("user migratable: " + vm.name)

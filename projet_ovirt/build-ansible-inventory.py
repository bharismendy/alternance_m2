#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import re

from my_ovirt import MyOVirt


shortcuts = {
    'dmz-lav': 'cluster=DMZ-Lavoisier',
    'dmz-fre': 'cluster=DMZ-Fremur',
    'lav':     'cluster=Lavoisier',
    'fre':     'cluster=Fremur'
}

queries = {
    'vms_lan':        'lav or fre',
    'vms_dmz':        'dmz-lav or dmz-fre',
    'vms_lav':        'lav or dmz-lav',
    'vms_fre':        'fre or dmz-fre',
    'vms_centos6':    'os=rhel_6x64',
    'vms_centos7':    'os=rhel_7x64',
    'vms_sles11':     'os=sles_11',
    'vms_debian7':    'os=debian_7',
    'vms_ubuntu1204': 'os=ubuntu_12_04',
    'vms_ubuntu1210': 'os=ubuntu_12_10',
    'vms_ubuntu1304': 'os=ubuntu_13_04',
    'vms_ubuntu1310': 'os=ubuntu_13_10',
    'vms_ubuntu1404': 'os=ubuntu_14_04',
    'hosts_lan':      'lav or fre',
    'hosts_dmz':      'dmz-lav or dmz-fre',
    'hosts_lav':      'lav or dmz-lav',
    'hosts_fre':      'fre or dmz-fre'
}
    
special = {
    re.compile(r'xeausout1'): 'xeausout1.hbgt',
    re.compile(r'xeausout2'): 'xeausout2.hbgt',
    re.compile(r'(^.*dtm.*$)'): r'\1.dtm49.paysdelaloire.net'
}


def get_dns_name(vm_name):
    for reg in special.keys():
        if reg.match(vm_name):
            return reg.sub(special[reg], vm_name)
    return vm_name
    

with MyOVirt() as ov:
    for entry, query in queries.items():
        print('[{}]'.format(entry))
        method_name = 'list_' + re.sub('^(vms|hosts)_.*$', r'\1', entry)

        for pattern in ['dmz-lav', 'dmz-fre', 'lav', 'fre']:
            query = re.sub(pattern, shortcuts[pattern], query)

        for item in getattr(ov, method_name)(query, only_up=True):
            print(get_dns_name(item))
        print()

print("""
[hosts:children]
hosts_lav
hosts_fre

[hosts:vars]
ansible_user=root
ansible_ssh_pass=ovirtcg49

[vms_centos:children]
vms_centos6
vms_centos7
""")

# vim: ts=4 sw=4 expandtab

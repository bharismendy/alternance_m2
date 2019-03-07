#!/usr/bin/python3.4
# -*- coding: utf-8 -*-

import re
import socket

from my_ovirt import MyOVirt

svm_list = [
    'engine.nfs.cg49.fr',
    'ged.nfs.cg49.fr',
    'ha-fre.nfs.cg49.fr',
    'ha-lav.nfs.cg49.fr',
    'isos.nfs.cg49.fr',
    'prod.nfs.cg49.fr',
    'sccm.nfs.cg49.fr',
    'test.nfs.cg49.fr'
]

print("# localhost")
print("127.0.0.1   localhost localhost.localdomain localhost4 localhost4.localdomain4")
print("::1         localhost localhost.localdomain localhost6 localhost6.localdomain6")

print("\n# oVirt nodes")
with MyOVirt() as ov:
    for host in ov.list_hosts():
        ip = socket.gethostbyname(host)
        shortname = re.sub(r'([^\.]+)\.cg49\.fr', r'\1', host)
        print(ip + "\t" + host + "\t" + shortname)

print("\n# ovirtengine")
ip = socket.gethostbyname("ovirtengine.cg49.fr")
print(ip + "\tovirtengine.cg49.fr\tovirtengine")


print("\n# Storage")
for svm in svm_list:
    ip = socket.gethostbyname(svm)
    shortname = re.sub(r'([^\.]+)\.nfs.cg49\.fr', r'\1.nfs', svm)
    print(ip + "\t" + svm + "\t" + shortname)

# vim: ts=4 sw=4 expandtab

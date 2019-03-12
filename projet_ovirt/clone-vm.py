#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
# the goal of this script is to automatically to delete vm on an ovirt server

import argparse
import argcomplete
from lib import crypt
from lib.config import Config
from lib.my_ovirt import MyOVirt
from importlib import import_module
import time
import ovirtsdk4.types as types
import random
import re
from lib.ipam_client import IpamClient
from lib.dnsmgr import DNSMgr


class ConfigVmCloner(Config):
    def __init__(self, cfg_file=None, with_ipam=True):
        super().__init__(cfg_file)
        self.ovirt = self.config['ovirtengine']
        self.ovirt['password'] = crypt.decode(self.ovirt['password'])
        self.zabbix = self.config['zabbix']
        self.zabbix['password'] = crypt.decode(self.zabbix['password'])
        if with_ipam:
            self.ipam = self.config['ipam']
            self.ipam['password'] = crypt.decode(self.ipam['password'])
            if self.ipam['verify'].lower() in ['yes', '1', 'true']:
                self.ipam['verify'] = True
            else:
                self.ipam['verify'] = False
            self.dnsmgr = self.config['dnsmgr']


def collect_args():
    """
    collect arguments from the command line and clean them
    :return: an object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help="nom de la vm", type=str)
    parser.add_argument('new_name', help="nom de la nouvelle vm", type=str)
    parser.add_argument('--datacenter', help="power off/on", action='store_true', default="Sysprod")
    parser.add_argument('--force', help="power off/on", action='store_true')
    parser.add_argument("--config", type=str, help="fichier de configuration")
    parser.add_argument(
        '--zone', help="zone réseau",
        choices=['lan-test', 'lan-prod', 'dmz-pub', 'dmz-test', 'dmz-hbgt', 'dmz-dtm'],
        default='lan-test'
    )
    parser.add_argument(
        '--domain_name', help="nom de domaine exemple .cg49.fr",
        default='.cg49.fr'
    )

    argcomplete.autocomplete(parser)
    return parser.parse_args()


def make_a_clone_vm(args):
    """
    function that delete a virtual machine on an ovirt server
    :param args: list of args getted and cleaned from the terminal
    :return: nothing
    """
    with MyOVirt() as ovirt:

        connection = ConfigVmCloner(args.config)

        # we start by finding the vm
        vms_service = ovirt.sys.vms_service()
        try:
            vm = vms_service.list(search=args.name)[0]
            if vm:
                vm_service = vms_service.vm_service(vm.id)
        except():
            print("/!\\VM not found " + args.name+"/!\\")
            exit(1)

        print("finding the cluster...")
        try:
            config = import_module('lib.'+args.datacenter.lower())
        except():
            print("/!\\can't retrieve configuration file /!\\")
            exit(1)

        try:
            cluster = None
            for element in config.cluster:
                if element[0] == args.zone:
                    cluster = config.cluster[element]
                    break
            if cluster is None:
                print("can't find the cluster ")

        except():
            print("/!\\ can't find the cluster /!\\")
        try:
            vm_exist = vms_service.list(search=args.new_name)
            if vm_exist:
                print("/!\\ clone with this name already exist ! /!\\")
                exit(1)
        except():
            print("/!\\ problem to access to the vm /!\\")
            exit(1)
    
        print("creating the snapshot...")
        try:
            description = "cloning snap " + str(random.randint(0, 1000000000))
            # Locate the service that manages the snapshots of the virtual machine:
            snapshots_service = vms_service.vm_service(vm.id).snapshots_service()
            snapshots_service.add(
                types.Snapshot(
                    description=description,
                    persist_memorystate=False),
                async = False
            )
            # Wait for snapshot to finish

        except():
            print("fail to create snapshot")
            exit(1)
        print("start cloning the machine...")
        try:
            # Find the snapshot. Note that the snapshots collection doesn't support
            # search, so we need to retrieve the complete list and the look for the
            # snapshot that has the description that we are looking for.
            snaps_service = vm_service.snapshots_service()
            snaps = snaps_service.list()
            found = False
            print("start searching for the snapshot", end='')
            while True:
                for s in snaps:
                    if s.description == description:
                        snap = s
                        found = True
                        break
                    else:
                        print(".", end='')
                if found:
                    print("")
                    break

            snap_service = snaps_service.snapshot_service(snap.id)
            print('Waiting until the snapshot is created, the status is now '+snap.snapshot_status.value, end='')
            # time.sleep(30)
            # uncomment in case of snapshot locked but displayed as not locked
            # report : https://bugzilla.redhat.com/show_bug.cgi?id=1628909
            while snap.snapshot_status != types.SnapshotStatus.OK:
                print(".", end='')
                time.sleep(6)
                snap = snap_service.get()
            print("\nstart cloning the VM...")
            # Create a new virtual machine, cloning it from the snapshot:
            cloned_vm = vms_service.add(
                vm=types.Vm(
                    name=args.new_name,
                    snapshots=[
                        types.Snapshot(
                            id=snap.id
                        )

                    ],
                    cluster=types.Cluster(
                            name=cluster
                    )
                )
            )

            # Find the service that manages the cloned virtual machine:
            cloned_vm_service = vms_service.vm_service(cloned_vm.id)

            # Wait till the virtual machine is down, as that means that the creation
            # of the disks of the virtual machine has been completed:
            while True:
                time.sleep(5)
                cloned_vm = cloned_vm_service.get()
                if cloned_vm.status == types.VmStatus.DOWN:
                    break
            print("destroying the Snapshot")
            snaps_service.snapshot_service(snap.id).remove()

        except():
            print("failed to clone the vm...")
            exit(1)

        # getting the new VM to configure it
        try:
            vm = vms_service.list(search=args.new_name)[0]
            if vm:
                vm_service = vms_service.vm_service(vm.id)
        except():
            print("/!\\VM not found " + args.new_name+"/!\\")
            exit(1)
            raise

        # renaming all the disk of the clone
        disk_attachments_service = vm_service.disk_attachments_service()
        test = disk_attachments_service.list()
        for el in test:
            # rename all the disk of the vm
            disks_service = ovirt.sys.disks_service()
            disk_service = disks_service.disk_service(el.id)
            disk = disk_service.get()
            current_name = disk.alias
            el.disk.alias = current_name.replace(args.name, args.new_name)
            disk_attachments_service.attachment_service(el.id).update(disk_attachment=el)

        # getting all network interfaces ²to unlinked them
        for nic in vm_service.nics_service().list():
            nic.linked = False
            vm_service.nics_service().nic_service(nic.id).update(nic=nic)

        print("finding the CIDR")
        try:
            os = vm_service.get().os.type
        except():
            print("/!\\can't retrieve configuration file /!\\")
            exit(1)
        try:
            if 'ubuntu' in os.lower():
                os = 'ubuntu1804'

            elif 'centos' or 'rhel' in os.lower():
                os = 'centos7'

            elif 'windows' in os.lower():
                os = 'windows'

            elif 'other' in os.lower():
                if re.match(r'^[x].$', args.new_name):
                    os = 'centos7'
                elif re.match(r'^[w].$', args.new_name):
                    os = 'windows'
                else:
                    raise Exception("impossible to guess the operating system")
            cidr = config.net_conf[args.zone]['subnet'][os]
        except ():
            print("/!\\can't retrieve os information and get the cidr /!\\")
        print("getting the fqdn :")
        try:
            # getting domain name
            domain_name = args.domain_name
            domain_name.strip()
            if not domain_name.startswith('.'):
                domain_name = '.' + domain_name
                print(domain_name)
            fqdn = args.new_name + domain_name
        except():
            print("can't get the FQDN")
            exit(1)

        print("requesting the ip address...")
        try:
            with IpamClient(**connection.ipam) as ipam:
                ip = ipam.reserve_address(hostname=fqdn, subnet_cidr=cidr)
        except():
            print("/!\\error during the register of the ip address /!\\")
            exit(1)

        print("register the A record in the DNS")
        try:
            dnsmgr = DNSMgr(**connection['dnsmgr'])
            dnsmgr.add_record(name=args.new_name, ip=ip)
        except():
            print("/!\\ can't register the A record /!\\")

        try:
            print("--------------------------------------------------")
            print("The ip address is : "+str(ip))
            print("The FQDN address is : "+str(fqdn))
            print("--------------------------------------------------")
        except():
            print("/!\\ no information to display /!\\")


if __name__ == '__main__':
    param = collect_args()
    make_a_clone_vm(args=param)

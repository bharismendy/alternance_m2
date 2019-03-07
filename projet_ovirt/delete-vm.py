# -*- coding: utf-8 -*-
# the goal of this script is to automatically to delete vm on an ovirt server

import argparse
import argcomplete
import socket
from lib import crypt
from lib.config import Config
from lib.ipam_client import IpamClient
from lib.dnsmgr import DNSMgr
from lib.my_ovirt import MyOVirt
import time
import ovirtsdk4.types as types
from zabbix.api import ZabbixAPI


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
    parser.add_argument('--force', help="power off/on", action='store_true')
    parser.add_argument("--config", type=str, help="fichier de configuration")

    argcomplete.autocomplete(parser)
    return parser.parse_args()


def delete_vm(args):
    """
    function that delete a virtual machine on an ovirt server
    :param args: list of args getted and cleaned from the terminal
    :return: nothing
    """
    with MyOVirt() as ovirt:
        cfg = ConfigVmCloner(args.config)

        # we start by finding the vm
        vms_service = ovirt.sys.vms_service()
        try:
            vm = vms_service.list(search=args.name)[0]
            if vm:
                vm_service = vms_service.vm_service(vm.id)
        except():
            print("/!\\VM not found " + args.name+"/!\\")
            exit(1)

        print("getting ip from fqdn...")
        try:
            fqdn = vm.fqdn
            ip = socket.gethostbyname(fqdn)
        except():
            print("impossible to get ip from the dns check your configuration !")
            exit(1)

        print("now we stop the server...")
        if args.force:
            vms_service.stop()
        else:
            vm_service.shutdown()
        while True:
            time.sleep(5)
            vm = vm_service.get()
            if vm.status == types.VmStatus.DOWN:
                break

        print("removing the dns record...")
        try:
            dnsmgr = DNSMgr(**cfg['dnsmgr'])
            # getting domain name
            domain_name = fqdn.replace(args.name+'.', '')
            dnsmgr.remove_record(name=args.name, ip=ip, domain=domain_name)
        except():
            print("/!\\error can't delete the DNS record !/!\\")
            exit(1)

        print("releasing the ip address...")
        try:
            with IpamClient(**cfg.ipam) as ipam:
                ipam.release_address(ip)
        except():
            print("/!\\error during the release of the ip !/!\\")
            exit(1)

        print("deleting the virtual machine ...")
        vm_service.remove()

        print("starting to delete the zabbix record ...")

        zapi = ZabbixAPI(url=cfg.zabbix['url'],
                         use_authenticate=False,
                         user=cfg.zabbix['username'],
                         password=cfg.zabbix['password'])

        hosts = zapi.host.get(filter={"host": fqdn})

        hostnames = [host['host'] for host in hosts]

        # if there is no problem we delete it
        if len(hostnames) == 1:
            id_host = [hosts[0]['hostid']]
            zapi.do_request(method='host.delete', params=id_host)
        else:
            print("/!\\ Problem on the number of host found on the Zabbix server /!\\")
            print("------- Here is the list --------")
            for element in hostnames:
                print(element)
            print("------- End of the list ---------")


if __name__ == '__main__':
    param = collect_args()
    delete_vm(args=param)

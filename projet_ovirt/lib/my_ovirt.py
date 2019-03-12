# -*- coding: utf-8 -*-

import re
from lib import crypt

import ovirtsdk4.types as types

from lib.config import Config
from lib import ovirt_services


class MyOVirtConfig(Config):
    def __init__(self, cfg_file=None, with_ipam=True):
        super().__init__(cfg_file)
        self.config['ovirtengine']['password'] = crypt.decode(self.config['ovirtengine']['password'])    
        self.ovirt = self.config['ovirtengine']
        self.room = {}
        for key in self.config.keys():
            m = re.match(r'^room:([^:]+):(.+)$', key)
            if m is not None:
                if m.group(1) not in self.room.keys():
                    self.room[m.group(1)] = {}
                self.room[m.group(1)][m.group(2)] = self.config[key]['clusters'].split(',')
        

class MyOVirt(ovirt_services.OVirtServices):
    def __init__(self, cfg_file=None):
        self.cfg = MyOVirtConfig(cfg_file=cfg_file)
        super().__init__(**self.cfg.ovirt)

    def list_vms(self, query=None, only_up=False):
        result = []

        if query is None:
            vms = self.sys.vms_service().list()
        else:
            vms = self.sys.vms_service().list(search=query)

        for vm in vms:
            if only_up and vm.status == types.VmStatus.DOWN:
                continue
            result.append("{}".format(vm.name))

        return result

    def list_hosts(self, query=None, only_up=False):
        result = []

        if query is None:
            vms = self.sys.hosts_service().list()
        else:
            vms = self.sys.hosts_service().list(search=query)

        for vm in vms:
            result.append("{}".format(vm.name))

        return result

    def shutdown_vm(self, vm_name, dc_name='Sysprod', wait=True):
        vm = self.get_vm(vm_name, dc_name)
        super().shutdown_vm(vm, wait)

    def poweroff_vm(self, vm_name, dc_name='Sysprod', wait=True):
        vm = self.get_vm(vm_name, dc_name)
        super().poweroff_vm(vm, wait)

    def start_vm(self, vm_name, dc_name='Sysprod', wait=True):
        vm = self.get_vm(vm_name, dc_name)
        super().start_vm(vm, wait)

    def print_vm(self, vm_name, dc_name='Sysprod'):
        vm = self.get_vm(vm_name, dc_name)
        topology = "CPU   {} cores  (sockets/cores/threads {}:{}:{})".format(
                vm.cpu.topology.sockets * vm.cpu.topology.cores * vm.cpu.topology.threads,
                vm.cpu.topology.sockets, vm.cpu.topology.cores, vm.cpu.topology.threads)
        if vm.memory < (1024 * 1024 * 1024):
            ram = "RAM   {:.0f}MB".format(vm.memory / (1024 * 1024))
        else:
            ram = "RAM   {:.0f}GB".format(vm.memory / (1024 * 1024 * 1024))
        os_type = "OS    {}".format(vm.os.type)
        print("{}\n{}\n{}".format(os_type, ram, topology))

    def tag_vm(self, vm_name, tags, dc_name='Sysprod'):
        vm = self.get_vm(vm_name, dc_name)
        super().tag_vm(vm, tags)

    def list_matching_tags(self, pattern):
        tags = []
        for tag in self.sys.tags_service().list():
            if re.match(pattern, tag.name):
                tags.append(tag.name)
        return tags

    def list_stop_tags(self):
        """Retourne la liste des tags Knn dans l'ordre croissant
        """
        return sorted(self.list_matching_tags(r'K\d\d'))

    def list_start_tags(self):
        """Retourne la liste des tags Snn dans l'ordre croissant
        """
        return sorted(self.list_matching_tags(r'S\d\d'))

    def list_vms_with_tag(self, tag, cluster_name=None, dc_name='Sysprod'):
        if cluster_name is None:
            search = 'datacenter={} and tag={}'.format(dc_name, tag)
        else:
            search = 'datacenter={} and cluster={} and tag={}'.format(dc_name, cluster_name, tag)
        return self.sys.vms_service().list(search=search)

    def is_guest_agent_installed(self, vm_name, dc_name='Sysprod'):
        vm = self.get_vm(vm_name, dc_name=dc_name)
        return vm.guest_operating_system is not None

    def list_tagged_vms_in_room(self, room, tag):
        clauses = []
        for datacenter in self.cfg.room[room].keys():
            for cluster in self.cfg.room[room][datacenter]:
                clauses.append('cluster = ' + cluster.strip() + ' and tag = ' + tag)
        search = ' or '.join(clauses)
        return self.sys.vms_service().list(search=search)

    def list_vms_in_room(self, room):
        clauses = []
        for datacenter in self.cfg.room[room].keys():
            for cluster in self.cfg.room[room][datacenter]:
                clauses.append('cluster = ' + cluster.strip())
        search = ' or '.join(clauses)
        return self.sys.vms_service().list(search=search)

    def stop_scenario(self, room):
        k_steps = self.list_stop_tags()
        vm_in_k, vm_with_stop_tag = {}, []
        for k_step in k_steps:
            vm_in_k[k_step] = self.list_tagged_vms_in_room(room, k_step)
            vm_with_stop_tag.append(vm_in_k[k_step])
        vm_in_k['---'] = list(filter(lambda x: x not in vm_with_stop_tag, self.list_vms_in_room(room)))
        k_steps.insert(0, '---')
        existing_steps = []
        for k_step in k_steps:
            if len(vm_in_k[k_step]) == 0:
                del(vm_in_k[k_step])
            else:
                existing_steps.append(k_step)
        return existing_steps, vm_in_k

    def display_stop_scenario(self, room):
        k_steps, vm_in_k = self.stop_scenario(room)
        for k_step in k_steps:
            print("<" + k_step + ">")
            for vm in vm_in_k[k_step]:
                status = vm.status.value
                guest = vm.guest_operating_system is not None
                if status == 'down':
                    status = 'NO START'
                else:
                    status = 'start'
                if guest:
                    guest = " guest ok"
                else:
                    guest = " NO GUEST"
                print("    {} ({}, {})".format(vm.name, status, guest))
            print()

    def enable_maintenance(self, dc_name='Sysprod'): 
        """Active le mode maintenance du HA sur l'engine
        """
        vm_he = self.get_vm('HostedEngine',dc_name=dc_name)
        self.sys.vms_service().vm_service(vm_he.id).maintenance(maintenance_enabled=True)        

    def disable_maintenance(self, dc_name='Sysprod'):
        """Désactive le mode maintenance du HA sur l'engine
        """
        vm_he = self.get_vm('HostedEngine',dc_name=dc_name)
        self.sys.vms_service().vm_service(vm_he.id).maintenance(maintenance_enabled=False)

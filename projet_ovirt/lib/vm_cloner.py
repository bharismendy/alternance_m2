# -*- coding: utf-8 -*-

import re

from lib import ovirt_services


class VMCloner(ovirt_services.OVirtServices):

    def __init__(self, vm_infos, **kwargs):
        super().__init__(**kwargs)
        for key, value in vm_infos.items():
            self.__setattr__(key, value)

    def do_basic_checking(self):
        # Vérifie que: le template existe, la vm n'existe pas, le cluster
        # le storage domain et le vnic_profile existent
        self.get_vm(self.source_vm_name, self.dc_name)
        try:
            self.get_vm(self.vm_name, self.dc_name)
            raise Exception(self.vm_name+' existe')
        except ovirt_services.NotFoundException:
            pass
        self.cluster = self.get_cluster(self.cluster_name)
        self.sd = self.get_storage_domain(self.sd_name, self.dc_name)
        self.vnic_profile = self.get_vnic_profile(self.vnic_name, self.dc_name)

    def set_source_disks(self, disks):
        for disk in disks:
            new_name = re.sub(
                r'^.+_([^_]+)$',
                self.vm_name + r'_\1',
                disk['name']
            )
            try:
                self.get_disk(new_name, self.dc_name)
                raise Exception('disk '+new_name+' existe')
            except ovirt_services.NotFoundException:
                disk['new_name'] = new_name
        self.disks = disks

    def create_vm(self, vm_infos):
        self.vm = super().create_vm(vm_infos)

    def add_nic(self, nic_name):
        self.add_nic_to_vm(self.vm, nic_name, self.vnic_profile)

    def tag_vm(self, tags):
        super().tag_vm(self.vm, tags)

    def copy_disks(self):
        for disk in self.disks:
            self.copy_disk(disk['id'], disk['new_name'], self.sd)

    def attach_disks(self):
        for item in self.disks:
            disk = self.get_disk(item['new_name'], self.dc_name)
            self.wait_disk_status(disk.id, 'OK')
            self.attach_disk(self.vm, disk.id, item['is_bootable'], True)

    def cloud_init(self):
        super().cloud_init(self.vm, self.net, self.fqdn)

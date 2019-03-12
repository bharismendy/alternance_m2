# -*- coding: utf-8 -*-

import logging
import time

import ovirtsdk4 as sdk
from ovirtsdk4 import types

my_script="""
write_files:
    - content: |
        systemctl disable cloud-init
        systemctl disable cloud-init-local
        systemctl disable cloud-config
        systemctl disable cloud-final
        systemctl stop cloud-init
        systemctl stop cloud-init-local
        systemctl stop cloud-config
        systemctl stop cloud-final
        rm /tmp/disable.sh
      path: /tmp/disable.sh
      permissions: '0777'
runcmd:
    - [ /tmp/disable.sh ]
"""


class OVirtServices:
    def __init__(self, url, username, password, insecure, ca_file, debug, connections, pipeline):
        self.connection = sdk.Connection(
            url=url,
            username=username,
            password=password,
            insecure=insecure,
            ca_file=ca_file,
            debug=debug,
            connections=int(connections),
            pipeline=int(pipeline),
            log=logging.getLogger()
        )
        self.sys = self.connection.system_service()

    def __enter__(self):
        return self

    def __exit__(self, typ, val, tb):
        self.close()

    def close(self):
        self.connection.close()

    def get_data_center(self, name):
        search = 'name=' + name
        data_centers = self.sys.data_centers_service().list(search=search)
        self.__check_unicity(data_centers, 'DataCenter', search)
        return data_centers[0]

    def get_cluster(self, name):
        search = 'name=' + name
        clusters = self.sys.clusters_service().list(search=search)
        self.__check_unicity(clusters, 'Cluster', search)
        return clusters[0]

    def get_storage_domain(self, sd_name, dc_name):
        search = 'name={} and datacenter={}'.format(sd_name, dc_name)
        sds = self.sys.storage_domains_service().list(search=search)
        self.__check_unicity(sds, 'Storage Domain', search)
        return sds[0]

    def get_vm(self, vm_name, dc_name):
        search = 'name={} and datacenter={}'.format(vm_name, dc_name)
        vms = self.sys.vms_service().list(search=search)
        self.__check_unicity(vms, 'Vm', search)
        return vms[0]

    def get_disk(self, disk_name, dc_name):
        search = 'name={} and datacenter={}'.format(disk_name, dc_name)
        vms = self.sys.disks_service().list(search=search)
        self.__check_unicity(vms, 'Disks', search)
        return vms[0]

    def get_vnic_profile(self, vp_name, dc_name):
        dc = self.get_data_center(dc_name)
        for vp in self.sys.vnic_profiles_service().list():
            if vp.name == vp_name:
                if self.__vp_in_datacenter(vp, dc):
                    return vp

        pseudo = 'name={} and datacenter={}'.format(vp_name, dc_name)
        raise NotFoundException(vp_name, pseudo)

    def collect_disks(self, vm_name, dc_name):
        disk_service = self.sys.disks_service().disk_service
        vm_service = self.sys.vms_service().vm_service

        vm = self.get_vm(vm_name, dc_name)
        das = vm_service(vm.id).disk_attachments_service()

        disks = []
        for disk_attachment in das.list():
            disk = disk_service(disk_attachment.disk.id).get()
            disks.append({
                'id': disk.id,
                'name': disk.name,
                'is_bootable': disk_attachment.bootable
            })
        return disks

    def copy_disk(self, src_id, dst_name, sd):
        new_disk = types.Disk(name=dst_name)
        srv = self.sys.disks_service().disk_service(src_id)
        srv.copy(disk=new_disk, storage_domain=sd)

    def wait_disk_status(self, disk_id, status_name):
        status = getattr(types.DiskStatus, status_name)
        disk_service = self.sys.disks_service().disk_service
        disk = disk_service(disk_id).get()
        while disk.status != status:
            time.sleep(5)
            disk = disk_service(disk_id).get()

    def attach_disk(self, vm, disk_id, is_bootable, activate):
        s = self.sys.vms_service().vm_service(vm.id).disk_attachments_service()
        s.add(types.DiskAttachment(
            bootable=is_bootable,
            disk=types.Disk(id=disk_id),
            interface=types.DiskInterface.VIRTIO,
            active=activate
        ))

    def create_vm(self, vm_info):
        return self.sys.vms_service().add(types.Vm(
            cpu=types.Cpu(topology=types.CpuTopology(
                sockets=vm_info.get('sockets', 1),
                cores=vm_info['cores'],
                threads=vm_info.get('threads', 1)
            )),
            cluster=types.Cluster(name=vm_info['cluster_name']),
            template=types.Template(name=vm_info.get('template', 'Blank')),
            name=vm_info['vm_name'],
            fqdn=vm_info['fqdn'],
            memory=vm_info['memory'],
            memory_policy=types.MemoryPolicy(
                ballooning=vm_info.get('ballooning', False),
                guaranteed=vm_info.get('guaranteed', vm_info['memory'])
            ),
            type=types.VmType('server'),
            soundcard_enabled=False,
            os=types.OperatingSystem(type=vm_info['os_code']),
        ))

    def add_nic_to_vm(self, vm, nic_name, vnic_profile):
        vm_srv = self.sys.vms_service().vm_service(vm.id)
        vm_srv.nics_service().add(types.Nic(
            name=nic_name,
            vnic_profile=types.VnicProfile(id=vnic_profile.id),
        ))

    def tag_vm(self, vm, tag_names):
        tag_srv = self.sys.vms_service().vm_service(vm.id).tags_service()
        for tag_name in tag_names:
            tag_srv.add(types.Tag(name=tag_name))

    def cloud_init(self, vm, net, fqdn, ):
        nic_configuration = types.NicConfiguration(
            name=net.get('ifname', 'eth0'),
            on_boot=net.get('on_boot', True),
            boot_protocol=types.BootProtocol.STATIC,
            ip=types.Ip(
                version=types.IpVersion.V4,
                address=net['ip'],
                netmask=net['netmask'],
                gateway=net['gateway']
            )
        )

        initialization = types.Initialization(
            nic_configurations=[nic_configuration],
            host_name=fqdn,
            dns_servers=' '.join(net['dns_servers']),
            dns_search=' '.join(net['dns_search']),
            custom_script=my_script,
        )

        vm_srv = self.sys.vms_service().vm_service(vm.id)
        vm_srv.start(
            use_cloud_init=True,
            vm=types.Vm(initialization=initialization)
        )

    def __vp_in_datacenter(self, vp, dc):
        net_id = vp.network.id
        net = self.sys.networks_service().network_service(net_id).get()
        if net.data_center.id == dc.id:
            return True
        else:
            return False

    def __check_unicity(self, array, entity, search):
        if len(array) > 1:
            raise NotUniqueException(entity, search)
        elif len(array) == 0:
            raise NotFoundException(entity, search)
    
    def shutdown_vm(self, vm, wait=True):
        self.sys.vms_service().vm_service(vm.id).shutdown(wait=wait)
    
    def poweroff_vm(self, vm, wait=True):
        self.sys.vms_service().vm_service(vm.id).stop(wait=wait)

    def start_vm(self, vm, wait=True):
        self.sys.vms_service().vm_service(vm.id).start(wait=wait)


class NotUniqueException(Exception):
    def __init__(self, entity, search):
        msg = "multiple {} results (search criteria: {})"
        super().__init__(msg.format(entity, search))


class NotFoundException(Exception):
    def __init__(self, entity, search):
        msg = "{} not found (search criteria: '{}')"
        super().__init__(msg.format(entity, search))

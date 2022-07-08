# Virtualized High Performance Computing Toolkit
#
# Copyright (c) 2018-2019 VMware, Inc. All Rights Reserved.
#
# This product is licensed to you under the Apache 2.0 license (the
# "License"). You may not use this product except in compliance with the
# Apache 2.0 License. This product may include a number of subcomponents with
#  separate copyright notices and license terms. Your use of these
# subcomponents is subject to the terms and conditions of the subcomponent's
# license, as noted in the LICENSE file.
# SPDX-License-Identifier: Apache-2.0
# coding=utf-8
from pyVmomi import vim
from pyVmomi import vmodl

from vhpc_toolkit import log
from vhpc_toolkit.wait import VMGetWait


class GetObjects(object):
    """
    A class for getting various vCenter objects

    """

    def __init__(self, content):
        """

        Args:
            content: vCenter retrieved content

        """

        self.content = content
        self.logger = log.my_logger(name=self.__class__.__name__)

    def get_container_view(self, vimtype):
        """Get the container view by managed object types

        Args:
            vimtype ([str]): a list of types to get container view

        Returns:
            [vmodl.ManagedObject]: a list of references to objects mapped by
                                    this view

        """

        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, vimtype, True
        )
        return container.view

    def get_obj(self, vimtype, name):
        """Get the managed object by name

        Args:
            vimtype ([str]): the list of managed types to get container view
            name (str): name of the obj that desired to get

        Returns:
            vmodl.ManagedObject: the managed object

        """

        obj = None
        for c in self.get_container_view(vimtype):
            if name:
                if c.name == name:
                    obj = c
                    break
            else:
                obj = c
                break
        return obj

    def get_datacenter(self, datacenter_name=None, _exit=True):
        """Get the datacenter managed object by name

        Args:
            datacenter_name (str): the name of datacenter to get
            _exit (bool): if not datacenter obj found, whether exit the program

        Returns:
            vim.Datacenter if exists

        """

        datacenter_obj = self.get_obj([vim.Datacenter], datacenter_name)
        if datacenter_obj:
            self.logger.info("Datacenter: {0}".format(datacenter_obj.name))
            return datacenter_obj
        else:
            self.logger.error("Cannot find datacenter {0}".format(datacenter_name))
            if _exit:
                raise SystemExit
            else:
                return None

    def get_folder(self, folder_name, _exit=True):
        """Get the folder managed object by name

        Args:
            folder_name (str): the name of folder to get
            _exit (bool)

        Returns:
            vim.Folder if exists

        """

        folder_obj = self.get_obj([vim.Folder], folder_name)
        if folder_obj:
            self.logger.info("Folder: {0}".format(folder_obj.name))
            return folder_obj
        else:
            self.logger.error("Cannot find folder {0}".format(folder_name))
            if _exit:
                raise SystemExit
            else:
                return None

    def get_cluster(self, cluster_name, _exit=True):
        """Get the cluster managed object by name

        Args:
            cluster_name (str): the name of cluster to get
            _exit (bool)

        Returns:
            vim.ClusterComputeResource if exists

        """

        cluster_obj = self.get_obj([vim.ClusterComputeResource], cluster_name)
        if cluster_obj:
            self.logger.info("Cluster: {0}".format(cluster_obj.name))
            return cluster_obj
        else:
            self.logger.error("Cannot find cluster {0}".format(cluster_name))
            if _exit:
                raise SystemExit
            else:
                return None

    def get_host(self, host_name, _exit=True):
        """Get the host managed object by name

        Args:
            host_name (str): the name of host to get
            _exit (bool)

        Returns:
            vim.HostSystem if exists

        """

        host_obj = self.get_obj([vim.HostSystem], host_name)
        if host_obj:
            self.logger.info("Host: {0}".format(host_obj.name))
            return host_obj
        else:
            self.logger.error("Cannot find host {0}".format(host_name))
            if _exit:
                raise SystemExit
            else:
                return None

    def get_host_by_vm(self, vm_obj):
        """Get the host managed object by vm

        Args:
            vm_obj (vim.VirtualMachine)

        Returns:
            vim.HostSystem if exists

        """

        container = self.content.viewManager.CreateContainerView(
            self.content.rootFolder, [vim.HostSystem], True
        )
        for host_obj in container.view:
            if vm_obj in host_obj.vm:
                return host_obj

    def get_datastore(self, datastore_name, _exit=True):
        """Get the host managed object by name

        Args:
            datastore_name (str): the name of datastore to get
             _exit (bool)

        Returns:
                vim.Datastore if exists

        """

        datastore_obj = self.get_obj([vim.Datastore], datastore_name)
        if datastore_obj:
            self.logger.info("Datastore: {0}".format(datastore_obj.name))
            return datastore_obj
        else:
            self.logger.error("Cannot find datastore {0}".format(datastore_name))
            if _exit:
                raise SystemExit
            else:
                return None

    def _get_resource_pool_from_host_or_cluster(
        self, resource_pool_name, host_name=None, cluster_name=None
    ):
        cluster_obj = None
        if host_name:
            cluster_obj = self.get_host(host_name).parent
        elif cluster_name:
            cluster_obj = self.get_cluster(cluster_name)

        if cluster_obj:
            for resource_pool in cluster_obj.resourcePool.resourcePool:
                if resource_pool.name == resource_pool_name:
                    return resource_pool

        return self.get_obj([vim.ResourcePool], resource_pool_name)

    def get_resource_pool(
        self,
        resource_pool_name,
        _exit=True,
        host_name: str = None,
        cluster_name: str = None,
    ):
        """Get the resource pool managed object by name. If there is conflict in resource pool name, it will try to
        get the resource pool belonging to the destination host, or the destination cluster in that order. Otherwise,
        it will get a random resource pool with the name

        Args:
            resource_pool_name (str): the name of resource pool to get
            host_name: Name of the host if resource pool belongs to a specific host
            cluster_name: Name of the cluster to which the resource pool belongs to
            _exit (bool)

        Returns:
            vim.ResourcePool if exists

        """
        resource_pool_obj = self._get_resource_pool_from_host_or_cluster(
            resource_pool_name, host_name=host_name, cluster_name=cluster_name
        )
        if resource_pool_obj:
            self.logger.info("Resource pool: {0}".format(resource_pool_obj.name))
            return resource_pool_obj
        else:
            self.logger.error(
                "Cannot find resource pool {0}".format(resource_pool_name)
            )
            if _exit:
                raise SystemExit
            else:
                return None

    def get_vm(self, vm_name, _exit=True):
        """Get the VM managed object by name

        Args:
            vm_name (str): the name of VM to get
            _exit (bool)

        Returns:
            vim.VirtualMachine if exists
        """

        vm_obj = self.get_obj([vim.VirtualMachine], vm_name)
        if vm_obj:
            self.logger.debug("Found vm {0}".format(vm_name))
            return vm_obj
        else:
            self.logger.error("Cannot find vm {0}".format(vm_name))
            if _exit:
                raise SystemExit
            else:
                return None

    def get_network(self, network_name, _exit=True):
        """Get the network managed object by name

        Args:
            network_name (str): the name of network to get
            _exit (bool)

        Returns:
            vim.Network if exists

        """

        network_obj = self.get_obj([vim.Network], network_name)
        if network_obj:
            self.logger.info("Found network {0}".format(network_name))
            return network_obj
        else:
            self.logger.error("Cannot find network {0}".format(network_name))
            if _exit:
                raise SystemExit
            else:
                return None

    def get_dvs(self, dvs_name, _exit=True):
        """Get the distributed virtual switch (DVS) managed object by name

        Args:
            dvs_name (str): the name of DVS to get
            _exit (bool)

        Returns:
            vim.dvs.VmwareDistributedVirtualSwitch if exists

        """

        dvs_obj = self.get_obj([vim.dvs.VmwareDistributedVirtualSwitch], dvs_name)
        if dvs_obj:
            self.logger.info("Found distributed " "virtual switch {0}".format(dvs_name))
            return dvs_obj
        else:
            self.logger.error(
                "Cannot find distributed virtual switch {0}".format(dvs_name)
            )
            if _exit:
                raise SystemExit
            else:
                return None


class GetDatacenter(object):
    """
    A class for getting datacenter properties

    """

    def __init__(self, datacenter_obj):
        """

        Args:
            datacenter_obj (vim.Datacenter)

        """

        self.datacenter_obj = datacenter_obj

    def compute_resources(self):
        """

        Returns:
            [vim.ManagedEntity] a list contains compute
                                    resources within this datacenter, including
                                    hosts and clusters

        """

        return self.datacenter_obj.hostFolder.childEntity

    def network_resources(self):
        """
        Returns:
                [vim.ManagedEntity]: a list contains the network resources within
                                     this datacenter, including Network,
                                     DistributedVirtualSwitch, and
                                     DistributedVirtualPortgroup objects.

        """

        return self.datacenter_obj.networkFolder.childEntity


class GetDVS(object):
    """
    A class for getting distributed virtual switch properties

    """

    def __init__(self, dvs_obj):
        """

        Args:
            dvs_obj (vim.dvs.VmwareDistributedVirtualSwitch)

        """

        self.dvs_obj = dvs_obj

    def dvs_pg_objs(self):
        """get all port group objects within this distributed virtual switch

        Args:

        Returns:
            [vim.dvs.DistributedVirtualPortgroup]

        """

        return [
            dvs_pg
            for dvs_pg in self.dvs_obj.portgroup
            if isinstance(dvs_pg, vim.dvs.DistributedVirtualPortgroup)
        ]


class GetCluster(object):
    """
    A class for getting cluster properties

    """

    def __init__(self, cluster_obj):
        """

        Args:
            cluster_obj (vim.ClusterComputeResource)

        """

        self.cluster_obj = cluster_obj

    def is_drs(self):
        """query DRS status

        Returns:
            bool: True if DRS is enabled otherwise False

        """

        return self.cluster_obj.configuration.drsConfig.enabled


class GetHost(object):
    """
    A class for getting host properties

    """

    def __init__(self, host_obj):
        """

        Args:
            host_obj (vim.ClusterComputeResource)

        """

        self.host_obj = host_obj
        self.logger = log.my_logger(name=self.__class__.__name__)

    def pci_obj(self, pci):
        """Get HostPciDevice object

        Args:
            pci (str): The name ID of this PCI, composed of "bus:slot.function"
                           e.g. '0000:84:00.0'

        Returns:
            vim.host.PciDevice: a PCI object if exists, otherwise None

        """

        for pciDevice in self.host_obj.hardware.pciDevice:
            if pci == pciDevice.id:
                pci_obj = pciDevice
                self.logger.info("Found PCI device {0}".format(pci))
                return pci_obj
        self.logger.info("Couldn't find PCI device {0}".format(pci))
        return None

    def pci_ids(self):
        """Get a list of available PCI device IDs on this host

        Returns:
            list: a list of PCI IDs if there are PCI devices on this host

        """

        return [device.id for device in self.host_obj.hardware.pciDevice]

    def network_obj(self, network):
        """Locate a Network on the host

        Args:
            network (str): The name of the network to locate

        Returns:
            vim.Network, a network object if exists, otherwise None

        """

        network_obj = None
        for network in self.host_obj.network:
            if network.name == network:
                network_obj = network
        if network_obj:
            self.logger.info(
                "Found network {0} on the host {1}".format(network, self.host_obj.name)
            )
        else:
            self.logger.info(
                "Couldn't network {0} on the host {1}".format(
                    network, self.host_obj.name
                )
            )
        return network_obj

    def shared_passthru_vgpu_types(self):
        """get the shared passthrough GPU types on the host

        Returns:
            Array: Array of shared passthru GPU types

        """

        return self.host_obj.config.sharedPassthruGpuTypes

    def pnics(self):
        """get all physical adapters on the host

        Returns:
            [vim.host.PhysicalNic]: a list of the physical network adapters
                                         of the host

        """

        return self.host_obj.configManager.networkSystem.networkInfo.pnic

    def vswitch(self):
        """get virtual switches on the host

        Returns:
                [HostVirtualSwitch]:  a list of virtual switches of the host

        """

        return self.host_obj.configManager.networkSystem.networkInfo.vswitch

    def cpu_mhz_per_core(self):
        """get cpu mhz per core for a host

        Returns:
            int: MHz per core on the host

        """

        return self.host_obj.summary.hardware.cpuMhz


class GetVM(object):
    """
    A class for getting VM properties

    """

    def __init__(self, vm_obj):
        """

        Args:
            vm_obj (VirtualMachine)

        """

        self.vm_obj = vm_obj
        self.logger = log.my_logger(name=self.__class__.__name__)

    def vm_name(self):
        """

        Returns:
            str: the name of the VM

        """

        return self.vm_obj.name

    def cpu_hotadd(self):
        """

        Returns:
            bool: True for CPU hotadd enabled o.w. False

        """

        return self.vm_obj.config.cpuHotAddEnabled

    def mem_hotadd(self):
        """

        Returns:
            bool: True for memory hotadd enabled o.w. False

        """

        return self.vm_obj.config.memoryHotAddEnabled

    def datacenter(self):
        """

        Returns:
            str: the name of the datacenter that the VM belongs to

        """

        return self.vm_obj.parent.parent.name

    def cluster(self):
        """

        Returns:
            str: the name of the cluster that VM belongs to

        """

        return self.vm_obj.resourcePool.parent.name

    def datastore(self):
        """

        Returns:
            str: the last datastore name for the VM

        """

        return self.vm_obj.datastore[-1].name

    def datastore_obj(self):
        """

        Returns:
            vim.Datastore: the last datastore managed object for the VM

        """

        return self.vm_obj.datastore[-1]

    def resource_pool(self):
        """

        Returns:
            str: The resource pool name for the VM

        """

        return self.vm_obj.resourcePool.name

    def resource_pool_obj(self):
        """

        Returns:
            vim.ResourcePool: the ResourcePool managed object for the VM

        """

        return self.vm_obj.resourcePool

    def folder(self):
        """

        Returns:
            str: the folder name for the VM

        """

        return self.vm_obj.parent.name

    def latency(self):
        """

        Returns:
            str: the latency sensitivity level for the vm

        """

        return (
            self.vm_obj.config.latencySensitivity.level
            if self.vm_obj.config.latencySensitivity is not None
            else "-"
        )

    def cpu(self):
        """

        Returns:
            int: number of CPUs for the VM

        """

        return self.vm_obj.config.hardware.numCPU

    def cpu_shares(self):
        """

        Returns:
            int: the CPU shares for the VM

        """

        return self.vm_obj.config.cpuAllocation.shares.shares

    def cores_per_socket(self):
        """

        Returns:
            int: The cores per socket for VM

        """

        return self.vm_obj.config.hardware.numCoresPerSocket

    def memory_shares(self):
        """

        Returns:
            int: the memory shares for the VM

        """

        return self.vm_obj.config.memoryAllocation.shares.shares

    def memory(self):
        """

        Returns:
            int: the memory in MB for the VM

        """

        return self.vm_obj.config.hardware.memoryMB

    def memory_in_gb(self):
        """

        Returns:
            int: the memory in GB for the VM

        """

        return float(self.memory()) / 1024

    def is_memory_reser_full(self):
        """

        Returns:
            bool: True if the VM's memory is fully reserved.

        """

        if self.memory_reser() == self.memory():
            return True
        else:
            return False

    def memory_reser(self):
        """

        Returns:
            int: the reserved memory in MB for the VM

        """

        return self.vm_obj.config.memoryAllocation.reservation

    def is_cpu_reser_full(self, host_cpu_mhz):
        """

        Args:
            host_cpu_mhz (int): MHz per core for the host of the VM

        Returns:
            bool: True if the VM has full reservation

        """
        return self.cpu_reser() == int(self.cpu() * host_cpu_mhz)

    def cpu_reser(self):
        """

        Returns:
            long: the amount of CPU reservation in mhz reserved by the VM

        """

        return self.vm_obj.config.cpuAllocation.reservation

    def is_power_on(self):
        """

        Returns:
            bool: True if the VM is powered on

        """

        return self.vm_obj.runtime.powerState == vim.VirtualMachinePowerState.poweredOn

    def network_obj(self, network_name, device_type=vim.VirtualVmxnet3):
        """

        Args:
            network_name (str): the network device name for the VM
            device_type (obj): the device type for the network device

        Returns:
            vim.Network: the Network adapter managed object located by the
                         network_name

        """

        network_obj = None
        network_type = None
        port_group_key = None
        for network in self.vm_obj.network:
            if network.name != network_name:
                continue
            if isinstance(network, vim.Network):
                network_type = "svs_pg"
            if isinstance(network, vim.DistributedVirtualPortgroup):
                port_group_key = network.key
                network_type = "dvs_pg"
        if network_type is None:
            return None
        for dev in self.vm_obj.config.hardware.device:
            if (
                network_type == "svs_pg"
                and isinstance(dev, device_type)
                and dev.deviceInfo.summary == network_name
            ):
                network_obj = dev
            elif (
                network_type == "dvs_pg"
                and isinstance(dev, device_type)
                and dev.backing.port.portgroupKey == port_group_key
            ):
                network_obj = dev
        return network_obj

    def device_objs_all(self):
        """
        Returns:
            a list of VM network objects [vim.Network]

        """
        return self.vm_obj.config.hardware.device

    def network_names(self):
        """
        Returns:
            list of str: the network names of the VM

        """

        return [network.name for network in self.vm_obj.network]

    def avail_pci_info(self):
        """
        Returns:
            a list of tuple: each tuple in the list contains
                            (device name, vendor name, device id, and sys id)

        """

        pci_devices = self.vm_obj.environmentBrowser.QueryConfigTarget(
            host=None
        ).pciPassthrough
        return [
            (
                pci_device.pciDevice.deviceName,
                pci_device.pciDevice.vendorName,
                pci_device.pciDevice.id,
                pci_device.systemId,
            )
            for pci_device in pci_devices
        ]

    def avail_pci_ids(self):
        """

        Returns:
            a list of str: a list of device IDs available for the VM

        """

        pci_devices = self.vm_obj.environmentBrowser.QueryConfigTarget(
            host=None
        ).pciPassthrough
        return [pci_device.pciDevice.id for pci_device in pci_devices]

    def existing_pci_ids(self):
        """

        Returns:
            a list of str: a list of Device IDs (Passthrough) existing in VMs

        """

        return [
            device.backing.id
            for device in self.vm_obj.config.hardware.device
            if isinstance(device, vim.VirtualPCIPassthrough)
            and hasattr(device.backing, "id")
        ]

    def configurable_pci_ids(self):
        """

        Returns:
            a set of str: a set of configurable device IDs for the VM

        """

        return set(self.avail_pci_ids()) - set(self.existing_pci_ids())

    def avail_sriov_info(self):
        """

        Returns:
            a list of tuple, which stores the info of SR-IOV devices for the VM

        """

        sriov_devices = self.vm_obj.environmentBrowser.QueryConfigTarget(
            host=None
        ).sriov
        return [
            (
                sriov_device.pnic,
                sriov_device.virtualFunction,
                sriov_device.pciDevice.deviceName,
                sriov_device.pciDevice.vendorName,
                sriov_device.pciDevice.id,
                sriov_device.systemId,
            )
            for sriov_device in sriov_devices
        ]

    def avail_sriov_ids(self):
        """

        Returns:
            a list of str: a list of SR-IOV device IDs available for the VM

        """

        sriov_devices = self.vm_obj.environmentBrowser.QueryConfigTarget(
            host=None
        ).sriov
        return [sriov_device.pciDevice.id for sriov_device in sriov_devices]

    def existing_sriov_ids(self):
        """

        Returns:
            a list of str: a list of device IDs (SR-IOV) existing in VMs

        """

        return [
            device.sriovBacking.physicalFunctionBacking.id
            for device in self.vm_obj.config.hardware.device
            if isinstance(device, vim.VirtualSriovEthernetCard)
            and hasattr(device, "sriovBacking")
        ]

    def configurable_sriov_ids(self):
        """

        Returns:
            a set of str: a set of configurable SR-IOV device IDs for the VM

        """

        return set(self.avail_sriov_ids()) - set(self.existing_sriov_ids())

    def existing_vgpu_profile(self):
        """

        Returns:
            str: the vGPU profile if exists o.w. None

        """

        for device in self.vm_obj.config.hardware.device:
            if isinstance(device, vim.VirtualPCIPassthrough) and hasattr(
                device.backing, "vgpu"
            ):
                return device.backing.vgpu
        return None

    def pci_id_sys_id_passthru(self):
        """

        Returns:
            dict: a dict stores {pci device id: system id}

        """

        pci_id_sys_id = {
            item.pciDevice.id: item.systemId
            for item in self.vm_obj.environmentBrowser.QueryConfigTarget(
                host=None
            ).pciPassthrough
        }
        return pci_id_sys_id

    def pci_id_sys_id_sriov(self):
        """

        Returns:
            dict: a dict stores {pci device id: system id}

        """

        pci_id_sys_id = {
            item.pciDevice.id: item.systemId
            for item in self.vm_obj.environmentBrowser.QueryConfigTarget(
                host=None
            ).sriov
        }
        return pci_id_sys_id

    def extra_config(self, config_key):
        """Query the extra config value with given config key

        Args:
            config_key (str): the config key to query config value

        Returns:
            str: the config value for the config key if exists; o.w. None

        """

        extra_configs = self.vm_obj.config.extraConfig
        for extra_config in extra_configs:
            if extra_config.key == config_key:
                return extra_config.value
        return None

    def uefi(self):
        """Check UEFI installation

        Returns:
            bool: True if VM is UEFI installed, False otherwise

        """

        return True if self.vm_obj.config.firmware == "efi" else False

    def pci_obj(self, pci):
        """Get PciDevice object

        Args:
            pci (str): The name ID of this PCI, composed of "bus:slot.function"

        Returns:
            vim.VirtualPCIPassthrough: the data object type contains PCI
                                           device info

        """

        for pciDevice in self.vm_obj.config.hardware.device:
            if (
                isinstance(pciDevice, vim.VirtualPCIPassthrough)
                and pciDevice.backing.id == pci
            ):
                pci_obj = pciDevice
                self.logger.info("Found PCI device {0}".format(pci))
                return pci_obj
        self.logger.info("Couldn't find PCI device {0}".format(pci))
        return None

    def sriov_obj(self, pf):
        """Get SR-IOV device object

        Args:
            pf (str): the name ID of this SR-IOV, composed of
                          "bus:slot.function"

        Returns:
            vim.VirtualSriovEthernetCard: the data object type contains the
                                               SR-IOV device info

        """

        for pciDevice in self.vm_obj.config.hardware.device:
            if (
                isinstance(pciDevice, vim.VirtualSriovEthernetCard)
                and pciDevice.sriovBacking.physicalFunctionBacking.id == pf
            ):
                sriov_obj = pciDevice
                self.logger.info("Found the physical function {0}".format(pf))
                return sriov_obj
        self.logger.info("Couldn't find the physical function {0}".format(pf))
        return None

    def vgpu_obj(self, vgpu_profile):
        """Get vGPU object

        Args:
            vgpu_profile (str): the vGPU profile

        Returns:
            vim.VirtualPCIPassthrough: the data object type contains PCI
                                           device info

        """

        for device in self.vm_obj.config.hardware.device:
            if isinstance(device, vim.VirtualPCIPassthrough) and hasattr(
                device.backing, "vgpu"
            ):
                if device.backing.vgpu == vgpu_profile:
                    vgpu_obj = device
                    self.logger.info("Found the vGPU profile {0}".format(vgpu_profile))
                    return vgpu_obj
        self.logger.info("Couldn't find the vGPU profile {0}".format(vgpu_profile))
        return None

    def get_ip_addr(self):
        """Get VM's IP

        Returns:
            str: VM's IP address if exists

        """

        vm_status_wait = VMGetWait(self.vm_obj)
        try:
            self.logger.info(
                "VM {0}'s IP address is {1}".format(
                    self.vm_obj.name, vm_status_wait.wait_for_ip()
                )
            )
        except RuntimeError:
            self.logger.warning("Can not get IP address")


class GetClone(GetObjects):
    """
    A class for getting VM clone objects

    """

    def __init__(
        self,
        content,
        template_obj,
        datacenter_name=None,
        folder_name=None,
        cluster_name=None,
        resource_pool_name=None,
        host_name=None,
        datastore_name=None,
        cpu=None,
        memory=None,
    ):
        """

        Args:
            content: vCenter retrieve content by ServiceInstance object
            template_obj (vim.VirtualMachine)
            datacenter_name (str): the dest datacenter name
            folder_name (str): the dest folder name
            cluster_name (str): the dest cluster name
            resource_pool_name (str): the dest resource pool name
            host_name (str): the dest host name
            datastore_name (str): the dest datastore name
            cpu (int): number of vCPUs; if none, it will be same as template VM
            memory (int): memory size in GB; if none, will will be same as
            template VM

        """

        super().__init__(content)

        # get the default datacenter
        self.dest_datacenter_obj = self.get_datacenter(datacenter_name)

        if folder_name:
            self.dest_folder_obj = self.get_folder(folder_name)
        else:
            self.dest_folder_obj = self.dest_datacenter_obj.vmFolder
            self.logger.info(
                "No VM folder specified. "
                "The first VM folder ({0}) "
                "in the datacenter ({1}) is "
                "used.".format(self.dest_folder_obj.name, self.dest_datacenter_obj.name)
            )

        if datastore_name:
            self.dest_datastore_obj = self.get_datastore(datastore_name)
        else:
            self.dest_datastore_obj = self.get_datastore(template_obj.datastore[0].name)
            self.logger.info(
                "No datastore specified. "
                "The same datastore ({0}) "
                "of the template ({1}) is used.".format(
                    self.dest_datastore_obj.name, template_obj.name
                )
            )

        if resource_pool_name:
            self.dest_resource_pool_obj = self.get_resource_pool(
                resource_pool_name, host_name=host_name, cluster_name=cluster_name
            )
        else:
            self.dest_resource_pool_obj = None
            self.logger.info(
                "No resource pool specified. Will use default resource pool."
            )

        if cluster_name:
            self.dest_cluster_obj = self.get_cluster(cluster_name)
        else:
            self.dest_cluster_obj = self.dest_datacenter_obj.hostFolder.childEntity[0]

        if host_name:
            self.dest_host_obj = self.get_host(host_name)
        elif GetCluster(self.dest_cluster_obj).is_drs():
            self.logger.info(
                "No host specified. "
                "DRS is enabled. "
                "A host selected by DRS will be used."
            )
            self.dest_host_obj = None
        else:
            self.dest_host_obj = None
            self.logger.warning(
                "No host specified and DRS is not enabled. "
                "The same host of the template "
                "in the cluster will be used."
            )
        if cpu:
            self.cpu = int(cpu)
        else:
            self.cpu = GetVM(template_obj).cpu()
        if memory:
            self.memory = int(float(memory) * 1024)
        else:
            self.memory = GetVM(template_obj).memory()

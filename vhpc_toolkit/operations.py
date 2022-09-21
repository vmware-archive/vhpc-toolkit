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
import itertools
import json
import logging
from typing import List

from distutils.util import strtobool
from pyVmomi import vim
from pyVmomi import vmodl
from textwrap3 import TextWrapper

from vhpc_toolkit import get_args
from vhpc_toolkit import log
from vhpc_toolkit.cluster import Check
from vhpc_toolkit.cluster import Cluster
from vhpc_toolkit.config_objs import ConfigDatacenter
from vhpc_toolkit.config_objs import ConfigDVS
from vhpc_toolkit.config_objs import ConfigHost
from vhpc_toolkit.config_objs import ConfigVM
from vhpc_toolkit.connect import Connect
from vhpc_toolkit.get_objs import GetClone
from vhpc_toolkit.get_objs import GetCluster
from vhpc_toolkit.get_objs import GetDatacenter
from vhpc_toolkit.get_objs import GetHost
from vhpc_toolkit.get_objs import GetObjects
from vhpc_toolkit.get_objs import GetVM
from vhpc_toolkit.view import View
from vhpc_toolkit.wait import GetWait
from vhpc_toolkit.wait import VMGetWait


class Operations(object):
    """
    All operations

    """

    def __init__(self, **kwargs):
        # get all operation configurations
        self.cfg, vcenter_cfg = get_args.get_global_config(kwargs)

        # connect to vCenter and retrieve service content
        self.content = Connect().connect_vcenter(
            server=vcenter_cfg["server"],
            username=vcenter_cfg["username"],
            password=vcenter_cfg["password"],
            port=int(vcenter_cfg["port"]),
            is_vault=vcenter_cfg.get("vault", False),
            vault_secret_path=vcenter_cfg.get("vault_secret_path", None),
        )

        # retrieve vCenter managed objects
        self.objs = GetObjects(self.content)

        # set logging level
        if self.cfg["debug"]:
            self.logger = log.my_logger(
                name=self.__class__.__name__, log_level=logging.DEBUG
            )
        else:
            self.logger = log.my_logger(name=self.__class__.__name__)

    @staticmethod
    def _extract_file(vm_cfg, file_keys=None):
        """
        unfold the file parsed from individual operations

        Args:
            vm_cfg (dict): the dict contains vm ops info
            file_keys (list): a list of keys to extract file which parsed
                              from individual operations

        Returns:
            list: a list of vm_cfgs
        """
        if file_keys is None:
            file_keys = ["vm"]
        vm_cfgs = []

        if Check().check_kv(vm_cfg, "vm"):
            vm_cfgs.append(vm_cfg)
        elif Check().check_kv(vm_cfg, "file"):
            try:
                f = open(vm_cfg["file"])
            except IOError:
                print("Failed to open file {0}".format(vm_cfg["file"]))
                raise SystemExit
            for line in f:
                if line.strip() and not line.startswith("#"):
                    for key in file_keys[: len(line.strip().split())]:
                        vm_cfg[key] = line.split()[file_keys.index(key)]
                    vm_cfgs.append(dict(vm_cfg))
            f.close()
        return vm_cfgs

    def view_cli(self):
        """
        view vCenter objects

        Returns:
            None
        """
        datacenters = self.objs.get_container_view([vim.Datacenter])
        # print basic information by default (compute resources)
        print("Basic View:")
        for datacenter in datacenters:
            print("|-+: {0} [Datacenter]".format(datacenter.name))
            for entity in GetDatacenter(datacenter).compute_resources():
                View(entity, cur_level=1).view_compute_resource()

        # print networking information (DVS, DPG)
        if self.cfg["networking"]:
            print("Networking:")
            for datacenter in datacenters:
                print("|-+: {0} [Datacenter]".format(datacenter.name))
                for entity in GetDatacenter(datacenter).network_resources():
                    View(entity, cur_level=1).view_network_resource()

# ========================= "Utility operations on one VM" =========================#

    # ~~~~~~~~~~~~~~~~~~~~~~~~ POWER ~~~~~~~~~~~~~~~~~~~~~~~~~#
    def power_cli(self):
        """
        Power on or off VMs

        Returns:
            None
        """
        vm_cfgs = self._extract_file(self.cfg)
        vms = [vm_cfg["vm"] for vm_cfg in vm_cfgs]

        if self.cfg["on"]:
            tasks = self._get_poweron_tasks(vms)
            GetWait().wait_for_tasks(tasks, task_name="Power on")
        
        if self.cfg["off"]:
            tasks = self._get_poweroff_tasks(vms)
            GetWait().wait_for_tasks(tasks, task_name="Power off")

    def _power_cluster(self, vm_cfgs, key):
        """
        Power on or off VMs (defined in cluster conf file)

        Returns:
            None
        """
        on_vms = []
        off_vms = []

        for vm_cfg in vm_cfgs:
            if Check().check_kv(vm_cfg, key) and vm_cfg[key] == "off":
                off_vms.append(vm_cfg["vm"])
            # default is to power on VMs unless off is specified
            else:
                on_vms.append(vm_cfg["vm"])
        if on_vms:
            tasks = self._get_poweron_tasks(on_vms)
            GetWait().wait_for_tasks(tasks, task_name="Power on")
        if off_vms:
            tasks = self._get_poweroff_tasks(off_vms)
            GetWait().wait_for_tasks(tasks, task_name="Power off")

    def _get_poweron_tasks(self, vms):
        """
        Power on VMs and get Tasks

        Args:
            vms (list): a list of VMs to power on

        Returns:
            list: a list of Tasks
        """
        tasks = []

        for vm in vms:
            vm_obj = self.objs.get_vm(vm)
            if not GetVM(vm_obj).is_power_on():
                task = ConfigVM(vm_obj).power_on()
                tasks.append(task)
            else:
                self.logger.info("VM {0} is already in power on state".format(vm))
        
        return tasks

    def _get_poweroff_tasks(self, vms):
        """
        Power off VMs and get Tasks

        Args:
            vms (list): a list of VMs to power off

        Returns:
            list: a list of Tasks
        """
        tasks = []

        for vm in vms:
            vm_obj = self.objs.get_vm(vm)
            if GetVM(vm_obj).is_power_on():
                task = ConfigVM(vm_obj).power_off()
                tasks.append(task)
            else:
                self.logger.info("VM {0} is already in power off state".format(vm))
        
        return tasks

    # ~~~~~~~~~~~~~~~~~~~~~~~ POWER END ~~~~~~~~~~~~~~~~~~~~~~#

    # ~~~~~~~~~~~~~~~~~~~~~ SECURE BOOT ~~~~~~~~~~~~~~~~~~~~~~#
    def _secure_boot_cluster(self, vm_cfgs, key):
        on_vms = []
        off_vms = []
        for vm_cfg in vm_cfgs:
            if key in vm_cfg:
                if vm_cfg[key]:
                    on_vms.append(vm_cfg["vm"])
                else:
                    off_vms.append(vm_cfg["vm"])

        if on_vms:
            GetWait().wait_for_tasks(
                self.__get_secure_boot_tasks(on_vms, enabled=True),
                task_name="Turn on secure boot",
            )
        if off_vms:
            GetWait().wait_for_tasks(
                self.__get_secure_boot_tasks(off_vms, enabled=False),
                task_name="Turn off secure boot",
            )

    def secure_boot_cli(self):
        """
        Turn on or off secure boot for VMs

        Returns:
            None
        """
        vm_cfgs = self._extract_file(self.cfg)
        vms = [vm_cfg["vm"] for vm_cfg in vm_cfgs]
        if self.cfg["on"]:
            tasks = self.__get_secure_boot_tasks(vms, True)
            GetWait().wait_for_tasks(tasks, task_name="Secure boot on")
        if self.cfg["off"]:
            tasks = self.__get_secure_boot_tasks(vms, False)
            GetWait().wait_for_tasks(tasks, task_name="Secure boot off")

    def __get_secure_boot_tasks(self, vms: List[str], enabled: bool) -> List[vim.Task]:
        """
        Enable/Disable secure boot for vms

        Args:
            vms: List of vm names
            enabled: Whether to enable secure boot or not

        Returns:
            List of task objects
        """
        tasks = []
        for vm in vms:
            vm_obj = self.objs.get_vm(vm)
            if GetVM(vm_obj).is_power_on():
                self.logger.info(
                    "VM {0} is turned on. So cannot change secure boot. Please turn off and try again".format(
                        vm
                    )
                )
            else:
                tasks.append(ConfigVM(vm_obj).change_secure_boot(enabled=enabled))

        return tasks

    # ~~~~~~~~~~~~~~~~~~~~ SECURE BOOT END ~~~~~~~~~~~~~~~~~~~~#

    # ~~~~~~~~~~~~~~~~~~~~~~~~CLONE~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def clone_cli(self):
        """
        clone VMs

        Returns:
            None
        """
        clone_file_keys = ["vm", "cluster", "host", "datastore"]
        # unfolding the file that is parsed from cli operations
        # if '--file' is not used, original cfg will be returned
        vm_cfgs = self._extract_file(self.cfg, file_keys=clone_file_keys)
        tasks = [self._get_clone_task(vm_cfg) for vm_cfg in vm_cfgs]
        # wait for all tasks to finish
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Clone VM")

    def _clone_cluster(self, vm_cfgs, *keys):
        """
        clone VMs (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts contains vm clone ops info
            *keys: a keyword array that can trigger this configuration

        Returns:
                None
        """
        tasks = [
            self._get_clone_task(vm_cfg)
            for vm_cfg in vm_cfgs
            if all(k in vm_cfg for k in keys)
        ]
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Clone VM")

    def _create_resource_pool(
            self, resource_pool_name, destination_host: vim.HostSystem
    ):
        resource_spec = vim.ResourceConfigSpec()
        resource_allocation_info = vim.ResourceAllocationInfo()
        resource_allocation_info.expandableReservation = True
        resource_allocation_info.reservation = 0
        resource_allocation_info.limit = -1
        resource_allocation_info.shares = vim.SharesInfo()
        resource_allocation_info.shares.level = vim.SharesInfo.Level.normal
        resource_spec.cpuAllocation = resource_allocation_info
        resource_spec.memoryAllocation = resource_allocation_info

        self.logger.warning(
            "Use default policy of resource pool creation. No limitation on CPU and memory allocation."
        )

        return destination_host.parent.resourcePool.CreateResourcePool(
            name=resource_pool_name, spec=resource_spec
        )

    def _get_clone_object(self, clone_dests, template_obj):
        # get the default datacenter
        dest_datacenter_obj = self.objs.get_datacenter(clone_dests["datacenter"])

        folder_name = clone_dests["vm_folder"]
        if folder_name:
            dest_folder_obj = self.objs.get_folder(folder_name)
        else:
            dest_folder_obj = dest_datacenter_obj.vmFolder
            self.logger.info(
                "No VM folder specified. "
                "The first VM folder ({0}) "
                "in the datacenter ({1}) is "
                "used.".format(dest_folder_obj.name, dest_datacenter_obj.name)
            )

        # get datastore
        datastore_name = clone_dests["datastore"]
        if datastore_name:
            dest_datastore_obj = self.objs.get_datastore(datastore_name)
        else:
            dest_datastore_obj = self.objs.get_datastore(template_obj.datastore[0].name)
            self.logger.info(
                "No datastore specified. "
                "The same datastore ({0}) "
                "of the template ({1}) is used.".format(
                    dest_datastore_obj.name, template_obj.name
                )
            )

        # get cluster
        cluster_name = clone_dests["cluster"]
        if cluster_name:
            dest_cluster_obj = self.objs.get_cluster(cluster_name)
        else:
            dest_cluster_obj = dest_datacenter_obj.hostFolder.childEntity[0]

        # get hosts
        host_name = clone_dests["host"]
        dest_host_obj = None
        if host_name:
            dest_host_obj = self.objs.get_host(host_name)
        elif GetCluster(dest_cluster_obj).is_drs():
            self.logger.info(
                "No host specified. "
                "DRS is enabled. "
                "A host selected by DRS will be used."
            )
        else:
            self.logger.warning(
                "No host specified and DRS is not enabled. "
                "The same host of the template "
                "in the cluster will be used."
            )

        # get resource pool
        resource_pool_name = clone_dests["resource_pool"]
        dest_resource_pool_obj = None
        if resource_pool_name:
            dest_resource_pool_obj = self.objs.get_resource_pool(
                resource_pool_name,
                _exit=False,
                host_name=host_name,
                cluster_name=cluster_name,
            )
            if dest_resource_pool_obj is None:
                self.logger.info(
                    f"Resource pool: {resource_pool_name} not found. So creating new resource pool"
                )
                dest_resource_pool_obj = self._create_resource_pool(
                    resource_pool_name, dest_host_obj
                )
        else:
            self.logger.info(
                "No resource pool specified. Will try to use default resource pool in destination cluster."
            )
            if dest_host_obj is not None:
                dest_resource_pool_obj = getattr(dest_host_obj.parent, "resourcePool")
            else:
                SystemExit(
                    "Resource pool and destination host name cannot both be empty"
                )

        # Change number of cores and memory if inputs are assigned
        cpu = clone_dests["cpu"]
        if cpu:
            cpu = int(cpu)
        else:
            cpu = GetVM(template_obj).cpu()

        memory = clone_dests["memory"]
        if memory:
            memory = int(float(memory) * 1024)
        else:
            memory = GetVM(template_obj).memory()

        return GetClone(
            content=self.content,
            datacenter_obj=dest_datacenter_obj,
            folder_obj=dest_folder_obj,
            cluster_obj=dest_cluster_obj,
            resource_pool_obj=dest_resource_pool_obj,
            host_obj=dest_host_obj,
            datastore_obj=dest_datastore_obj,
            cpu=cpu,
            memory=memory,
        )

    def _get_clone_task(self, vm_cfg):
        """
        clone VM and get task

        Args:
            vm_cfg (dict): a dict contains vm clone info

        Returns:
            Task
        """
        template_obj = self.objs.get_vm(vm_cfg["template"])
        if template_obj:
            dest_vm_name = vm_cfg["vm"]
            self.logger.info("Creating clone task for VM {0}".format(dest_vm_name))
            clone_dests = {}
            for clone_dest in [
                "datacenter",
                "vm_folder",
                "cluster",
                "resource_pool",
                "host",
                "datastore",
                "cpu",
                "memory",
            ]:
                if Check().check_kv(vm_cfg, clone_dest, required=False):
                    clone_dests[clone_dest] = vm_cfg[clone_dest]
                else:
                    clone_dests[clone_dest] = None
            # get clone dest objs
            clone_objs = self._get_clone_object(clone_dests, template_obj)
            # linked clone
            if Check().check_kv(vm_cfg, "linked"):
                task = ConfigVM(template_obj).linked_clone(
                    dest_vm=dest_vm_name,
                    host_obj=clone_objs.dest_host_obj,
                    folder_obj=clone_objs.dest_folder_obj,
                    resource_pool_obj=clone_objs.dest_resource_pool_obj,
                    cpu=clone_objs.cpu,
                    mem=clone_objs.memory,
                )

            # full clone
            else:
                task = ConfigVM(template_obj).full_clone(
                    dest_vm_name=dest_vm_name,
                    host_obj=clone_objs.dest_host_obj,
                    datastore_obj=clone_objs.dest_datastore_obj,
                    vm_folder_obj=clone_objs.dest_folder_obj,
                    resource_pool_obj=clone_objs.dest_resource_pool_obj,
                    cpu=clone_objs.cpu,
                    mem=clone_objs.memory,
                )
            return task
        else:
            self.logger.error(
                "Can not find clone template {0}.".format(vm_cfg["template"])
            )
            raise SystemExit

    # ~~~~~~~~~~~~~~~~~~~~ CLONE END~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

    # ~~~~~~~~~~~~~~~~~~~~~~~~ DESTROY ~~~~~~~~~~~~~~~~~~~~~~~~~#
    def destroy_cli(self):
        """
        destroy VMs

        Returns:
            None
        """
        vm_cfgs = self._extract_file(self.cfg)
        vms = [vm_cfg["vm"] for vm_cfg in vm_cfgs]

        if vms:
            try:
                confirm = input(
                    "[ACTION] Do you really want to destroy {0} ? ".format(vms)
                )
                if strtobool(confirm) == 1:
                    tasks = self._get_destroy_tasks(vms)
                    if tasks:
                        GetWait().wait_for_tasks(tasks, task_name="Destroy VM")
                elif strtobool(confirm) == 0:
                    self.logger.info("Not destroying any VMs")
            except ValueError:
                self.logger.info("Not a valid answer")
        else:
            self.logger.warning("No VMs specified to destroy")

    def _get_destroy_tasks(self, vms):
        """
        destroy VM and get task

        Args:
            vms (list): a list of vm names for destroy

        Returns:
            list: a list of destroy Tasks
        """
        vm_objs = []
        power_tasks = []

        # Check whether VMs are powered off
        for vm in vms:
            vm_obj = self.objs.get_vm(vm, _exit=False)
            if vm_obj is not None:
                vm_objs.append(vm_obj)
                if vm_obj.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                    power_tasks.append(ConfigVM(vm_obj).power_off())
        if power_tasks:
            GetWait().wait_for_tasks(
                power_tasks, task_name="Power off VMs before destroying"
            )
        
        # Destroy VMs
        destroy_tasks = [ConfigVM(vm_obj).destroy() for vm_obj in vm_objs]

        return destroy_tasks

    # ~~~~~~~~~~~~~~~~~~~~~~~ DESTROY END ~~~~~~~~~~~~~~~~~~~#

    #~~~~~~~~~~~~~~~~~~~~~ MIGRATE ~~~~~~~~~~~~~~~~~~~~~~~~~~#

    def migrate_vm_cli(self):
        tasks = []
        for vm_cfg in self._extract_file(self.cfg):
            vm_obj = self.objs.get_vm(vm_cfg["vm"])
            host_obj = self.objs.get_host(self.cfg["destination"])
            self.logger.info(
                f"Migrating VM {vm_cfg['vm']} to host {self.cfg['destination']}"
            )
            if GetVM(vm_obj).is_power_on():
                self.logger.info(
                    f"VM {vm_cfg['vm']} is powered on. So migration task might take some time"
                )
            tasks.append(ConfigVM(vm_obj).migrate_vm(host_obj))

        GetWait().wait_for_tasks(tasks, task_name="Migrate VM(s)")

    #~~~~~~~~~~~~~~~~~~~~~ MIGRATE END ~~~~~~~~~~~~~~~~~~~~~#

    # ~~~~~~~~~~~~~~~~~~~~~~~ POST ~~~~~~~~~~~~~~~~~~~~~~~~~~#

    def post_cli(self):
        """
        Execute post scripts for VM(s)

        Returns:
            None
        """
        if not Check().check_kv(self.cfg, "guest_password"):
            import getpass

            self.cfg["guest_password"] = getpass.getpass(
                "[ACTION] Please enter password for Guest OS(s): "
            )
        tasks = []
        vm_cfgs = self._extract_file(self.cfg)
        for vm_cfg in vm_cfgs:
            vm_obj = self.objs.get_vm(vm_cfg["vm"])
            if GetVM(vm_obj).is_power_on():
                self.logger.info("VM {0} is powered on. Good.".format(vm_obj.name))
            else:
                self.logger.info(
                    "VM {0} is not powered on. "
                    "Powering on it first.".format(vm_obj.name)
                )
                tasks.append(ConfigVM(vm_obj).power_on())
        GetWait().wait_for_tasks(tasks, task_name="Power on VM")
        procs = []
        for vm_cfg in vm_cfgs:
            Check().check_kv(vm_cfg, "guest_username", required=True)
            Check().check_kv(vm_cfg, "guest_password", required=True)
            procs.extend(
                self._get_post_procs(
                    vm_cfg["guest_username"],
                    vm_cfg["guest_password"],
                    vm_cfg["vm"],
                    vm_cfg["script"],
                )
            )
        if Check().check_kv(self.cfg, "wait"):
            proc_mng = self.content.guestOperationsManager.processManager
            GetWait().wait_for_procs(proc_mng, procs)

    def _get_post_procs(self, username, password, vm, scripts):
        """
        Execute the post script(s) in a VM and return process to track

        Args:
            username (str): the username of the VM guest OS
            password (str): the password for the VM guest OS
            vm (str): the VM name for post execution
            scripts (list): a list of scripts with full path for post execution

        Returns:
            a list of tuples, each element in tuple has post execution info
        """
        procs = []
        vm_obj = self.objs.get_vm(vm)
        vm_update = ConfigVM(vm_obj)
        vm_status = VMGetWait(vm_obj)
        proc_mng = self.content.guestOperationsManager.processManager
        guest_operations_manager = self.content.guestOperationsManager
        if vm_status.wait_for_vmtools():
            for script in scripts:
                proc = vm_update.execute_script(
                    proc_mng,
                    guest_operations_manager,
                    self.objs.get_host_by_vm(vm_obj),
                    script,
                    username,
                    password,
                )
                procs.append(proc)
        return procs

    # ~~~~~~~~~~~~~~~~~~~~ POST END ~~~~~~~~~~~~~~~~~~~~~~~#

# ======================= "Utility operations on one VM" End ===========================#

# ================ "Operations to change compute resources on one VM" ==================#

    # ~~~~~~~~~~~~~~~~~~~~~~~ CPUMEM ~~~~~~~~~~~~~~~~~~~~~~~~#
    def cpumem_cli(self):
        """
        Configure VM CPU or mem

        Returns:
            None
        """
        cpumem_tasks = []
        cpumem_reser_tasks = []
        vm_cfgs = self._extract_file(self.cfg)

        # Configure CPU and memory size for the VM(s)
        for vm_cfg in vm_cfgs:
            cpumem_tasks.extend(self._get_cpumem_tasks(vm_cfg))
        if cpumem_tasks:
            GetWait().wait_for_tasks(cpumem_tasks, task_name="Configure CPU/memory")

        # Configure CPU shares
        cpu_shares_tasks = [self._get_cpu_shares_task(vm_cfg) for vm_cfg in vm_cfgs]
        if cpu_shares_tasks:
            GetWait().wait_for_tasks(cpu_shares_tasks, task_name="Configure CPU shares")

        # Configure memory shares
        memory_shares_tasks = [
            self._get_memory_shares_task(vm_cfg) for vm_cfg in vm_cfgs
        ]
        if memory_shares_tasks:
            GetWait().wait_for_tasks(
                memory_shares_tasks, task_name="Configure memory shares"
            )
        
        # Configure CPU or memory reservation
        for vm_cfg in vm_cfgs:
            cpumem_reser_tasks.extend(self._get_cpumem_reser_tasks(vm_cfg))
        if cpumem_reser_tasks:
            GetWait().wait_for_tasks(
                cpumem_reser_tasks,
                task_name="Configure CPU/memory reservation",
            )

    def _cpumem_cluster(self, vm_cfgs, *keys):
        """
        Configure VM CPU or Mem (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts may contain vm cpu mem ops info
            *keys: a keyword array that can trigger this configuration

        Returns:
                None
        """
        tasks = []

        for vm_cfg in vm_cfgs:
            if all(k in vm_cfg for k in keys):
                tasks.extend(self._get_cpumem_tasks(vm_cfg))
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Configure CPU/memory")

    # ~~~~~~~~~~~~~~~~~~~~~~~ CPUMEM END~~~~~~~~~~~~~~~~~~~~~~#

    # ~~~~~~~~~~~~~~~~~~~~~~~ CPUSHARES ~~~~~~~~~~~~~~~~~~~~~~#
    def _cpu_shares_cluster(self, vm_cfgs, *keys):
        """
        set CPU shares for VMs (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts may contain cpu shares ops info
            *keys: a keyword array that can trigger this configuration

        Returns:
            None

        """
        tasks = [
            self._get_cpu_shares_task(vm_cfg)
            for vm_cfg in vm_cfgs
            if all(k in vm_cfg for k in keys)
        ]
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Configure CPU shares")

    def _memory_shares_cluster(self, vm_cfgs, *keys):
        """
        set memory shares for VMs (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts may contain memory shares ops info
            *keys: a keyword array that can trigger this configuration

        Returns:
            None
        """
        tasks = [
            self._get_memory_shares_task(vm_cfg)
            for vm_cfg in vm_cfgs
            if all(k in vm_cfg for k in keys)
        ]
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Configure memory shares")

    def _cpumem_reser_cluster(self, vm_cfgs, *keys):
        """
        set CPU or Mem reservations (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts may contain cpu mem reser ops info
            *keys: a keyword array that can trigger this configuration

        Returns:
                None
        """
        tasks = []
        for vm_cfg in vm_cfgs:
            if any(k in vm_cfg for k in keys):
                tasks.extend(self._get_cpumem_reser_tasks(vm_cfg))
        if tasks:
            GetWait().wait_for_tasks(
                tasks, task_name="Configure CPU/memory reservation"
            )

    def _get_cpumem_tasks(self, vm_cfg):
        """
        set CPU or Mem for a VM and get tasks

        Args:
            vm_cfg (dict): a dict contains vm config info

        Returns:
            list: a list of CPU or Mem Reconfigurtion Tasks
        """
        tasks = []
        vm_obj = self.objs.get_vm(vm_cfg["vm"])

        if Check().check_kv(vm_cfg, "cpu"):
            if GetVM(vm_obj).cpu() != vm_cfg["cpu"]:
                self.logger.info(
                    "Creating CPU re-configure " "task for VM {0}".format(vm_obj.name)
                )
                tasks.append(ConfigVM(vm_obj).cpus(vm_cfg["cpu"]))
            else:
                self.logger.info(
                    "No change of number of " "CPUs for VM {0}".format(vm_obj.name)
                )

        if Check().check_kv(vm_cfg, "memory"):
            mem = int(float(vm_cfg["memory"]) * 1024)
            if GetVM(vm_obj).memory() != mem:
                self.logger.info(
                    "Creating memory re-configure "
                    "task for VM {0}".format(vm_obj.name)
                )
                tasks.append(ConfigVM(vm_obj).memory(mem))
            else:
                self.logger.info(
                    "No change of memory size for VM {0}".format(vm_obj.name)
                )
        
        if Check().check_kv(vm_cfg, "cores_per_socket"):
            cores_per_socket = vm_cfg["cores_per_socket"]
            if GetVM(vm_obj).cores_per_socket() != cores_per_socket:
                self.logger.info(
                    "Creating cores per socket re-configure "
                    "task for VM {0}".format(vm_obj.name)
                )
                tasks.append(ConfigVM(vm_obj).cores_per_socket(cores_per_socket))
            else:
                self.logger.info(
                    "No change of cores per socket for VM {0}".format(vm_obj.name)
                )
        
        return tasks

    def _get_cpu_shares_task(self, vm_cfg):
        """
        set CPU shares for a VM and return Task

        Args:
            vm_cfg (dict): a dict contains vm config info

        Returns:
            Task
        """
        vm_obj = self.objs.get_vm(vm_cfg["vm"])

        if Check().check_kv(vm_cfg, "cpu_shares"):
            if GetVM(vm_obj).cpu_shares() != vm_cfg["cpu_shares"]:
                self.logger.info(
                    "Configuring CPU Shares for VM {0}".format(vm_obj.name)
                )
                task = ConfigVM(vm_obj).cpu_shares(vm_cfg["cpu_shares"])
                return task
            else:
                self.logger.info(
                    "No change of CPU Shares for VM {0}".format(vm_obj.name)
                )

    def _get_memory_shares_task(self, vm_cfg):
        """
        set memory shares for a VM and return Task

        Args:
            vm_cfg (dict): a dict contains vm config info

        Returns:
            Task
        """
        vm_obj = self.objs.get_vm(vm_cfg["vm"])

        if Check().check_kv(vm_cfg, "memory_shares"):
            if GetVM(vm_obj).memory_shares() != vm_cfg["memory_shares"]:
                self.logger.info(
                    "Configuring memory Shares for VM {0}".format(vm_obj.name)
                )
                task = ConfigVM(vm_obj).memory_shares(vm_cfg["memory_shares"])
                return task
            else:
                self.logger.info(
                    "No change of memory Shares for VM {0}".format(vm_obj.name)
                )

    def _get_cpumem_reser_tasks(self, vm_cfg):
        """
        set CPU or Mem Reservation and get Task

        Args:
            vm_cfg (dict): a dict contains vm config info

        Returns:
            a list of Tasks: a list of Task object
        """
        tasks = []
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        host_obj = self.objs.get_host_by_vm(vm_obj)
        vm_status = GetVM(vm_obj)
        vm_update = ConfigVM(vm_obj)

        if Check().check_kv(vm_cfg, "cpu_reservation", none_check=False):
            if vm_cfg["cpu_reservation"]:
                host_cpu_mhz = GetHost(host_obj).cpu_mhz_per_core()
                if (
                        vm_status.is_cpu_reser_full(host_cpu_mhz)
                        != vm_cfg["cpu_reservation"]
                ):
                    self.logger.info("Reserving CPU for VM {0}".format(vm_obj.name))
                    host_cpu_mhz = GetHost(host_obj).cpu_mhz_per_core()
                    tasks.append(
                        vm_update.cpu_reservation(host_cpu_mhz=host_cpu_mhz, reser=1)
                    )
                else:
                    self.logger.info(
                        "CPU is already reserved " "for VM {0}".format(vm_obj.name)
                    )
            else:
                if vm_status.cpu_reser():
                    self.logger.info(
                        "Removing CPU reservation for VM {0}".format(vm_cfg["vm"])
                    )
                    tasks.append(vm_update.cpu_reservation(reser=0))
                else:
                    self.logger.info(
                        "CPU is already not reserved for VM {0}".format(vm_obj.name)
                    )

        if Check().check_kv(vm_cfg, "memory_reservation", none_check=False):
            if vm_cfg["memory_reservation"]:
                if vm_status.is_memory_reser_full() != vm_cfg["memory_reservation"]:
                    self.logger.info("Reserving memory for VM {0}".format(vm_obj.name))
                    tasks.append(
                        vm_update.memory_reservation(vm_cfg["memory_reservation"])
                    )
                else:
                    self.logger.info(
                        "Memory is already reserved for VM {0}".format(vm_obj.name)
                    )
            else:
                if vm_status.memory_reser():
                    self.logger.info(
                        "Removing memory reservation for " "VM {0}".format(vm_obj.name)
                    )
                    tasks.append(vm_update.memory_reservation(reser=0))
                else:
                    self.logger.info(
                        "Memory is already not reserved for " "{0}".format(vm_obj.name)
                    )

        return tasks
    #~~~~~~~~~~~~~~~~~~ CPU & MEM SHARES END ~~~~~~~~~~~~~~~#

    # ~~~~~~~~~~~~~~~~~~~~~~~ LATENCY ~~~~~~~~~~~~~~~~~~~~~~#
    def latency_cli(self):
        """
        Configure latency sensitivity for VM(s)

        Returns:
            None
        """
        vm_cfgs = self._extract_file(self.cfg)
        tasks = [self._get_latency_task(vm_cfg) for vm_cfg in vm_cfgs]
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Configure latency sensitivity")
            self._latency_high(vm_cfgs)

    def _latency_cluster(self, vm_cfgs, key):
        """
        Configure latency sensitivity for VM(s)
        (defined in a cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts contains VM config info
            key: the keyword that can trigger this configuration

        Returns:
            None
        """
        tasks = []
        for vm_cfg in vm_cfgs:
            if key in vm_cfg:
                vm_cfg["level"] = vm_cfg[key]
                tasks.append(self._get_latency_task(vm_cfg))
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Configure latency sensitivity")
            self._latency_high(vm_cfgs)

    def _get_latency_task(self, vm_cfg):
        """
        Set Latency Sensitivity level and get task

        Args:
            vm_cfg (dict): a dict contains VM config info

        Returns:
            Task
        """
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        if Check().check_kv(vm_cfg, "check"):
            self.logger.info(
                "Latency sensitivity level is {0} for "
                "VM {1}".format(GetVM(vm_obj).latency(), vm_cfg["vm"])
            )
        if Check().check_kv(vm_cfg, "level"):
            task = ConfigVM(vm_obj).latency(vm_cfg["level"])
            return task

    def _latency_high(self, vm_cfgs):
        """
        setting CPU or Mem reservation if latency sensitivity set to high

        Args:
            vm_cfgs (list): a list of dicts contains VM config info

        Returns:
            None
        """
        tasks = []
        for vm_cfg in vm_cfgs:
            vm_obj = self.objs.get_vm(vm_cfg["vm"])
            vm_status = GetVM(vm_obj)
            if vm_status.latency() == "high":
                if vm_status.is_memory_reser_full():
                    self.logger.info(
                        "Good. Memory is already reserved for "
                        "VM {0}.".format(vm_obj.name)
                    )
                else:
                    self.logger.warning(
                        "Latency sensitivity "
                        "set to high requires "
                        "memory reservation"
                    )
                    self.logger.info("Reserving memory for VM {0}".format(vm_obj.name))
                    tasks.append(ConfigVM(vm_obj).memory_reservation(reser=1))
                host_obj = self.objs.get_host_by_vm(vm_obj)
                host_cpu_mhz = GetHost(host_obj).cpu_mhz_per_core()
                if vm_status.is_cpu_reser_full(host_cpu_mhz):
                    self.logger.info(
                        "Good. CPU is already reserved "
                        "for VM {0}".format(vm_obj.name)
                    )
                else:
                    self.logger.warning(
                        "Latency sensitivity "
                        "set to high requires "
                        "full CPU reservation"
                    )
                    self.logger.info("Reserving CPU for VM {0}".format(vm_obj.name))
                    tasks.append(
                        ConfigVM(vm_obj).cpu_reservation(host_cpu_mhz, reser=1)
                    )
        if tasks:
            GetWait().wait_for_tasks(
                tasks, task_name="Configure memory/CPU reservation"
            )

    # ~~~~~~~~~~~~~~~~~~~~~~~ LATENCY END ~~~~~~~~~~~~~~~~~~#

    #~~~~~~~~~~~~~~~~~~~~~~ AFFINITY ~~~~~~~~~~~~~~~~~~~~~~~#
    def vm_scheduling_affinity_cli(self):
        vm_cfgs = self._extract_file(self.cfg)
        vms = [vm_cfg["vm"] for vm_cfg in vm_cfgs]

        # If clear flag is set, clear the affinity
        if self.cfg["clear"]:
            self.cfg["affinity"] = []

        tasks = []
        for vm in vms:
            vm_obj = self.objs.get_vm(vm)
            if GetVM(vm_obj).is_power_on():
                self.logger.error(
                    "Could not change affinity for VM {0}. Please power off VM and try again".format(
                        vm
                    )
                )
            else:
                tasks.append(
                    ConfigVM(vm_obj).change_vm_scheduling_affinity(self.cfg["affinity"])
                )

        GetWait().wait_for_tasks(tasks, task_name="Set VM scheduling affinity")

    def numa_affinity_cli(self):
        vm_cfgs = self._extract_file(self.cfg)
        vms = [vm_cfg["vm"] for vm_cfg in vm_cfgs]

        # If clear flag is set, clear the affinity
        if self.cfg["clear"]:
            self.cfg["affinity"] = []

        tasks = []
        for vm in vms:
            vm_obj = self.objs.get_vm(vm)
            if GetVM(vm_obj).is_power_on():
                self.logger.error(
                    "Could not change NUMA affinity for VM {0}. Please power off VM and try again".format(
                        vm
                    )
                )
            else:
                tasks.append(
                    ConfigVM(vm_obj).change_numa_affinity(self.cfg["affinity"])
                )

        GetWait().wait_for_tasks(tasks, task_name="Set NUMA node affinity")

    #~~~~~~~~~~~~~~~~~~~~~~ AFFINITY END ~~~~~~~~~~~~~~~~~~~~#

# ==================== ==="Network related operations on one VM" =======================#

    # ~~~~~~~~~~~~~~~~~~~~ NETWORK ~~~~~~~~~~~~~~~~~~~~~~~~#
    def network_cli(self):
        """
        Add/Remove network adapters for VM(s)

        Returns:
             None
        """
        tasks = []
        vm_cfgs = self._extract_file(self.cfg)
        if self.cfg["add"]:
            for vm_cfg in vm_cfgs:
                tasks.extend(self._get_network_add_tasks(vm_cfg))
            if tasks:
                GetWait().wait_for_tasks(tasks, task_name="Add network adapter(s)")
        if self.cfg["remove"]:
            for vm_cfg in vm_cfgs:
                tasks.extend(self._get_network_remove_tasks(vm_cfg))
            if tasks:
                GetWait().wait_for_tasks(tasks, task_name="Remove network adapter(s)")

    def _network_cluster(self, vm_cfgs, *keys):
        """
        Add/Remove network adapters for VM(s) (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts may contain vm cpu mem ops info
            *keys: a keyword array that can trigger this configuration

        Returns:
            None
        """
        tasks = []

        for vm_cfg in vm_cfgs:
            if all(k in vm_cfg for k in keys):
                tasks.extend(self._get_network_add_tasks(vm_cfg))
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Add network adapter(s)")

    def _get_network_add_tasks(self, vm_cfg):
        """
        Add network adapter for a VM and get Task

        Args:
            vm_cfg (dict): a dict contains vm config info

        Returns:
            list: a list of add network adapter tasks
        """
        tasks = []
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        pgs = vm_cfg["port_group"]

        if isinstance(pgs, str):
            pgs = [pgs]
        for pg in pgs:
            pg_obj = self.objs.get_network(pg, dvs_name=vm_cfg.get("dvs_name"))
            if pg in GetVM(vm_obj).network_names():
                self.logger.warning(
                    "Port group {0} already exists on VM "
                    "{1}. "
                    "Skipping".format(pg, vm_cfg["vm"])
                )
                continue
            tasks.append(ConfigVM(vm_obj).add_network_adapter(pg_obj))
        return tasks

    def _get_network_remove_tasks(self, vm_cfg):
        """
        Remove network adapter for a VM and get Tasks

        Args:
            vm_cfg (dict): a dict contains vm config info

        Returns:
            list: a list of remove network adapter tasks
        """
        tasks = []
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        pgs = vm_cfg["port_group"]

        if isinstance(pgs, str):
            pgs = [pgs]
        for pg in pgs:
            pg_obj = GetVM(vm_obj).network_obj(pg)
            if pg_obj:
                self.logger.info(
                    "Found port group {0} " "for VM {1}".format(pg, vm_obj.name)
                )
                tasks.append(ConfigVM(vm_obj).remove_network_adapter(pg_obj))
            else:
                self.logger.error(
                    "Couldn't find port group {0} "
                    "on VM {1} to remove".format(pg, vm_obj.name)
                )
        return tasks

    # ~~~~~~~~~~~~~~~~~~~~~ NETWORK END ~~~~~~~~~~~~~~~~~~~~~#

    # ~~~~~~~~~~~~~~~~~~~~~ NETWORK CFG ~~~~~~~~~~~~~~~~~~~~~~~~#

    def network_cfg_cli(self):
        """
        Configure network properties for VM(s)

        Returns:
            None
        """
        vm_cfgs = self._extract_file(self.cfg)
        tasks = [self._get_network_cfg_task(vm_cfg) for vm_cfg in vm_cfgs]

        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Configure network properties")

    def _network_cfg_cluster(self, vm_cfgs, *keys):
        """
        Configure network properties for VM(s)
        (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts contains ops info
            *keys: a keyword array that can trigger this configuration

        Returns:
            None
        """
        tasks = []

        for vm_cfg in vm_cfgs:
            if any(k in vm_cfg for k in keys):
                tasks.append(self._get_network_cfg_task(vm_cfg))
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Configure network properties")

    def _get_network_cfg_task(self, vm_cfg):
        """
        Configure network property for a a VM and get Task

        Args:
            vm_cfg (dict): a dict contains vm config info

        Returns:
            Task
        """
        vm_obj = self.objs.get_vm(vm_cfg["vm"])

        if GetVM(vm_obj).is_power_on():
            self.logger.error(
                "VM {0} is powered on. "
                "Can not configure network in power on state. "
                "Skip.".format(vm_obj.name)
            )
            return
        Check().check_kv(vm_cfg, "port_group", required=True)
        network_obj = GetVM(vm_obj).network_obj(vm_cfg["port_group"])
        if network_obj:
            self.logger.info(
                "Found {0} for VM {1}".format(vm_cfg["port_group"], vm_obj.name)
            )
        else:
            self.logger.error(
                "Cannot find {0} for VM {1}. Skip.".format(
                    vm_cfg["port_group"], vm_obj.name
                )
            )
            return
        netmask = vm_cfg["netmask"] if Check().check_kv(vm_cfg, "netmask") else None
        gateway = vm_cfg["gateway"] if Check().check_kv(vm_cfg, "gateway") else None
        domain = vm_cfg["domain"] if Check().check_kv(vm_cfg, "domain") else None
        dns = vm_cfg["dns"] if Check().check_kv(vm_cfg, "dns") else None
        guest_hostname = (
            vm_cfg["guest_hostname"]
            if Check().check_kv(vm_cfg, "guest_hostname")
            else None
        )
        if Check().check_kv(vm_cfg, "is_dhcp"):
            if vm_cfg["is_dhcp"]:
                ip = None
            else:
                Check().check_kv(vm_cfg, "ip", required=True)
                ip = vm_cfg["ip"]
        else:
            Check().check_kv(vm_cfg, "ip", required=True)
            ip = vm_cfg["ip"]

        task = ConfigVM(vm_obj).config_networking(
            network_obj, ip, netmask, gateway, domain, dns, guest_hostname
        )

        return task

    # ~~~~~~~~~~~~~~~~~~~~~~~ NETWORK CFG END ~~~~~~~~~~~~~~~~~~~~~~~~~#

# ======================= Operations to add various devices on one VM ====================#

    # ~~~~~~~~~~~~~~~~~~~~~~~~~ PASSTHRU ~~~~~~~~~~~~~~~~~~~~~~~~#

    def passthru_cli(self):
        """
        Configure devices in Passthrough mode for VM(s)

        Returns:
            None
        """
        vm_cfgs = self._extract_file(self.cfg)
        if self.cfg["query"]:
            for vm_cfg in vm_cfgs:
                self._query_passthru(vm_cfg)
        if self.cfg["add"]:
            tasks = []
            for vm_cfg in vm_cfgs:
                tasks.extend(self._get_add_passthru_task(vm_cfg))
            if tasks:
                GetWait().wait_for_tasks(tasks, task_name="Add Passthrough device(s)")
        if self.cfg["remove"]:
            tasks = []
            for vm_cfg in vm_cfgs:
                tasks.extend(self._get_remove_passthru_task(vm_cfg))
            if tasks:
                GetWait().wait_for_tasks(
                    tasks, task_name="Remove Passthrough device(s)"
                )

    def _passthru_cluster(self, vm_cfgs, *keys):
        """
        Configure devices in Passthrough mode for VM(s)
        (defined in a cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts contains VM config info
            *keys: a keyword array that can trigger this configuration

        Returns:
            None
        """
        tasks = []
        for vm_cfg in vm_cfgs:
            if all(k in vm_cfg for k in keys):
                tasks.extend(self._get_add_passthru_task(vm_cfg))
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Add Passthrough device(s)")

    def _query_passthru(self, vm_cfg):
        """
        Query Passthrough device(s) for a VM

        Args:
            vm_cfg (dict): a dict contains VM config info

        Returns:
            None
        """
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        vm_status = GetVM(vm_obj)
        devices = vm_status.avail_pci_info()
        if devices:
            print("Available Passthrough device(s) for VM {0}:".format(vm_obj.name))
            print("------------------------------------------------")
            for index, pci_device in enumerate(devices):
                device_name, vendor_name, device_id, system_id = pci_device
                print("device # {0}".format(index))
                wrapper = TextWrapper(initial_indent=" " * 4)
                print(wrapper.fill("device name = {0}".format(device_name)))
                print(wrapper.fill("vendor name = {0}".format(vendor_name)))
                print(wrapper.fill("device id = {0}".format(device_id)))
                print(wrapper.fill("system id = {0}\n".format(system_id)))
        else:
            print("No available Passthrough " "devices for VM {0}".format(vm_obj.name))

    def _get_add_passthru_task(self, vm_cfg):
        """
        Add device(s) in Passthrough mode for a VM and get Task

        Args:
            vm_cfg (dict): a dict contains VM config info

        Returns:
            list: a list of Tasks
        """
        tasks = []
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        vm_update = ConfigVM(vm_obj)
        vm_status = GetVM(vm_obj)
        host_obj = self.objs.get_host_by_vm(vm_obj)
        Check().check_kv(vm_cfg, "device", required=True)
        mmio_size = None
        if Check().check_kv(vm_cfg, "mmio_size"):
            if not self.is_valid_mmio_size(vm_cfg["mmio_size"]):
                self.logger.warning(
                    "mmio_size has to be power of 2 and "
                    "larger than 0. "
                    "This value will be ignored. "
                    "The default mmio_size (256) will be used"
                )
            else:
                mmio_size = vm_cfg["mmio_size"]
        for device in vm_cfg["device"]:
            device = device.lower()
            if device in vm_status.configurable_pci_ids():
                self.logger.debug(
                    "Device {0} is available for " "VM {1}".format(device, vm_obj.name)
                )
                tasks.extend(
                    vm_update.add_pci(
                        device,
                        host_obj,
                        vm_update,
                        vm_status,
                        mmio_size,
                        dynamic_direct_io=bool(vm_cfg.get("dynamic")),
                    )
                )
            else:
                if device in vm_status.existing_pci_ids():
                    self.logger.error(
                        "Device {0} is already configured. " "Skip.".format(device)
                    )
                elif device not in vm_status.avail_pci_ids():
                    self.logger.error(
                        "Device {0} is not available "
                        "for VM {1}. Skip.".format(device, vm_obj.name)
                    )
                    self._query_passthru(vm_cfg)
        if tasks:
            if not vm_status.is_memory_reser_full():
                self.logger.warning(
                    "Adding a PCI device or shared PCI device "
                    "in passthrough mode needs to reserve memory. "
                    "Reserving memory."
                )
                tasks.append(vm_update.memory_reservation(reser=1))
            else:
                self.logger.debug("Good. Memory is already reserved.")
        return tasks

    @staticmethod
    def is_valid_mmio_size(num):
        """check MMIO size setting is valid"""

        return num > 0 and ((num & (num - 1)) == 0)

    def _get_remove_passthru_task(self, vm_cfg):
        """
        Remove Passthrough device from a VM and get Task

        Args:
            vm_cfg (dict): a dict contains VM config info

        Returns:
            list: a list of Tasks
        """
        tasks = []
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        vm_status = GetVM(vm_obj)
        vm_update = ConfigVM(vm_obj)
        Check().check_kv(vm_cfg, "device", required=True)
        for device in vm_cfg["device"]:
            device = device.lower()
            if device in vm_status.existing_pci_ids():
                self.logger.info(
                    "Device {0} to be removed " "on VM {1}".format(device, vm_cfg["vm"])
                )
                tasks.append(vm_update.remove_pci(device, vm_status))
            else:
                self.logger.error(
                    "Couldn't find device {0} "
                    "on VM {1}. "
                    "Skip.".format(device, vm_cfg["vm"])
                )
        return tasks

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PASSTHRU END ~~~~~~~~~~~~~~~~~~~~~#

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~ SRIOV ~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def sriov_cli(self):
        """
        Configure device in SR-IOV mode for VM

        Returns:
            None
        """
        vm_cfgs = self._extract_file(self.cfg)
        if self.cfg["query"]:
            for vm_cfg in vm_cfgs:
                self._query_sriov(vm_cfg)
        if self.cfg["add"]:
            tasks = []
            for vm_cfg in vm_cfgs:
                tasks.extend(self._get_add_sriov_tasks(vm_cfg))
            if tasks:
                GetWait().wait_for_tasks(tasks, task_name="Add SR-IOV device(s)")
        if self.cfg["remove"]:
            tasks = []
            for vm_cfg in vm_cfgs:
                task = self._get_remove_sriov_tasks(vm_cfg)
                if task:
                    tasks.append(task)
            if tasks:
                GetWait().wait_for_tasks(tasks, task_name="Remove SR-IOV device(s)")

    def _sriov_cluster(self, vm_cfgs, *keys):
        """
        Configure device in SR-IOV mode for VM(s)
        (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts contains VM config info
            *keys: a keyword array that can trigger this configuration

        Returns:
                None
        """
        tasks = []
        for vm_cfg in vm_cfgs:
            if all(k in vm_cfg for k in keys):
                tasks.extend(self._get_add_sriov_tasks(vm_cfg))
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Add SR-IOV device(s)")

    def _query_sriov(self, vm_cfg):
        """
        query available SR-IOV devices for a VM

        Args:
                vm_cfg (dict): a dict contains VM config info

        Returns:
                None
        """
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        vm_status = GetVM(vm_obj)
        devices = vm_status.avail_sriov_info()
        if devices:
            print("Available Passthrough device(s) " "for VM {0}:".format(vm_obj.name))
            print("------------------------------------------------")
            for index, pci_device in enumerate(devices):
                pnic, vf, device_name, vendor_name, device_id, system_id = pci_device
                print("device # {0}".format(index))
                wrapper = TextWrapper(initial_indent=" " * 4)
                print(wrapper.fill("PNIC = {0}".format(pnic)))
                print(wrapper.fill("Virtual Function = {0}".format(vf)))
                print(wrapper.fill("device name = {0}".format(device_name)))
                print(wrapper.fill("vendor name = {0}".format(vendor_name)))
                print(wrapper.fill("device id = {0}".format(device_id)))
                print(wrapper.fill("system id = {0}\n".format(system_id)))
        else:
            print("No available SR-IOV devices for VM {0}".format(vm_obj.name))

    def _get_add_sriov_tasks(self, vm_cfg):
        """
        Add device in SR-IOV mode for a VM and get Tasks

        Args:
            vm_cfg (dict): a dict contains VM config info

        Returns:
            list: a list of Tasks
        """
        tasks = []
        dvs_obj = None
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        host_obj = self.objs.get_host_by_vm(vm_obj)
        vm_update = ConfigVM(vm_obj)
        # verify whether this PF has SR-IOV capability
        device_ids = GetVM(vm_obj).avail_sriov_ids()

        Check().check_kv(vm_cfg, "pf", required=True)
        Check().check_kv(vm_cfg, "sriov_port_group", required=True)

        # Converting to list to make sure it supports adding multiple SR-IOV at once
        if isinstance(vm_cfg["pf"], str):
            vm_cfg["pf"] = [vm_cfg["pf"]]

        if isinstance(vm_cfg["sriov_port_group"], str):
            vm_cfg["sriov_port_group"] = [vm_cfg["sriov_port_group"]]

        # Need to ensure length of pf and sriov port group is same
        if len(vm_cfg["pf"]) != len(vm_cfg["sriov_port_group"]):
            self.logger.error("Number of pf and sriov port groups must be the same")
            raise SystemExit

        # If you add dvs for one of the SR-IOV, need to add it to all of them
        if len(vm_cfg["pf"]) > 1 and len(vm_cfg["sriov_port_group"]) != len(
                vm_cfg.get("sriov_dvs_name", [])
        ):
            self.logger.error(
                "When adding multiple SRIOV, cannot leave dvs name empty for any resource"
            )
            raise SystemExit

        if "sriov_dvs_name" in vm_cfg:
            # If there is only one sriov_dvs_name, convert it to list
            if isinstance(vm_cfg["sriov_dvs_name"], str):
                vm_cfg["sriov_dvs_name"] = [vm_cfg["sriov_dvs_name"]]
        else:
            vm_cfg["sriov_dvs_name"] = [None]

        vm_cfg["sriov_dvs_name"] = vm_cfg.get("sriov_dvs_name", None)

        for pf, pg, dvs_name in itertools.zip_longest(
                vm_cfg["pf"], vm_cfg["sriov_port_group"], vm_cfg["sriov_dvs_name"]
        ):
            pf_obj = GetHost(host_obj).pci_obj(pf)
            pg_obj = self.objs.get_network(pg, dvs_name=dvs_name)
            if dvs_name is not None:
                dvs_obj = self.objs.get_dvs(dvs_name)
                self.logger.info("Found dvs {0}".format(dvs_name))
            if pf in device_ids:
                self.logger.info(
                    "Find physical function {0} for VM {1} "
                    "and this physical function is SR-IOV capable".format(
                        pf, vm_obj.name
                    )
                )
                tasks.append(
                    vm_update.add_sriov_adapter(
                        pg_obj,
                        pf_obj,
                        dvs_obj,
                        allow_guest_os_mtu_change=bool(
                            vm_cfg.get("allow_guest_mtu_change", 0)
                        ),
                    )
                )
            else:
                self.logger.error(
                    "This physical function is not SR-IOV capable. " "Skipping"
                )
        if tasks:
            if not GetVM(vm_obj).is_memory_reser_full():
                self.logger.warning(
                    "Add a SR-IOV device needs to reserve memory. " "Reserving memory."
                )
                tasks.append(vm_update.memory_reservation(reser=1))
            else:
                self.logger.debug("Good. Memory is already reserved.")
        return tasks

    def _get_remove_sriov_tasks(self, vm_cfg):
        """
        Remove SR-IOV device from a VM

        Args:
            vm_cfg (dict): a dict contains vm config info

        Returns:
            Task
        """
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        if Check().check_kv(vm_cfg, "pf"):
            pf = vm_cfg["pf"]
            pf_obj = GetVM(vm_obj).sriov_obj(pf)
            try:
                task = ConfigVM(vm_obj).remove_sriov_adapter(pf_obj)
                return task
            except KeyError:
                self.logger.error(f"Could not find pf {pf}")
                return None
        elif Check().check_kv(vm_cfg, "sriov_port_group"):
            pg = vm_cfg["sriov_port_group"]
            pg_obj = GetVM(vm_obj).network_obj(
                network_name=pg, device_type=vim.vm.device.VirtualSriovEthernetCard
            )
            if pg_obj:
                self.logger.debug(
                    "Found port group {0} for VM {1}".format(pg, vm_obj.name)
                )
                task = ConfigVM(vm_obj).remove_network_adapter(pg_obj)
                return task
            else:
                self.logger.error(
                    "Couldn't find SR-IOV port group {0} "
                    "on VM {1} to remove".format(pg, vm_obj.name)
                )
                return None
        else:
            self.logger.error(
                "Please specify either the name of SR-IOV port "
                "group or the Physical Function backs the "
                "SR-IOV port group for device removal."
            )
            return None

    #~~~~~~~~~~~~~~~~~~~~~~ SRIOV END ~~~~~~~~~~~~~~~~~~~~~~#

    #~~~~~~~~~~~~~~~~~~~~~ vGPU ~~~~~~~~~~~~~~~~~~~~~~~#

    def vgpu_cli(self):
        """
        Configure vGPU profile for VM(s)

        Returns:
            None
        """
        vm_cfgs = self._extract_file(self.cfg)
        if self.cfg["query"]:
            for vm_cfg in vm_cfgs:
                self._query_vgpu(vm_cfg)
        if self.cfg["add"]:
            tasks = []
            for vm_cfg in vm_cfgs:
                tasks.extend(self._get_add_vgpu_tasks(vm_cfg))
            if tasks:
                GetWait().wait_for_tasks(tasks, task_name="Add a vGPU profile")
        if self.cfg["remove"]:
            tasks = []
            for vm_cfg in vm_cfgs:
                tasks.extend(self._get_remove_vgpu_tasks(vm_cfg))
            if tasks:
                GetWait().wait_for_tasks(tasks, task_name="Remove vGPU profile")

    def _vgpu_cluster(self, vm_cfgs, *keys):
        """
        Configure vGPU profile for VM(s) (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts contains VM config info
            *keys: a keyword array that can trigger this configuration

        Returns:
                None
        """
        tasks = []

        for vm_cfg in vm_cfgs:
            if all(k in vm_cfg for k in keys):
                vm_cfg["profile"] = vm_cfg["vgpu"]
                tasks.extend(self._get_add_vgpu_tasks(vm_cfg))
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Add vGPU profile")

    def _query_vgpu(self, vm_cfg):
        """
        Query available vGPU profiles for a VM

        Args:
            vm_cfg (dict): a dict contains VM config info

        Returns:
            None
        """
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        host_obj = self.objs.get_host_by_vm(vm_obj)
        vgpu_profiles = GetHost(host_obj).shared_passthru_vgpu_types()
        
        if vgpu_profiles:
            print("Available vGPU profiles for VM {0}:".format(vm_obj.name))
            for vgpu_profile in vgpu_profiles:
                wrapper = TextWrapper(initial_indent=" " * 4)
                print(wrapper.fill(vgpu_profile))
        else:
            print("No available vGPU profiles for VM {0}".format(vm_obj.name))

    def _get_add_vgpu_tasks(self, vm_cfg):
        """
        Add vGPU profile for a VM and get Task

        Args:
            vm_cfg (dict): a dict contains VM config info

        Returns:
            list: a list of Tasks
        """
        tasks = []
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        vm_update = ConfigVM(vm_obj)
        vm_status = GetVM(vm_obj)
        host_obj = self.objs.get_host_by_vm(vm_obj)

        Check().check_kv(vm_cfg, "profile", required=True)
        if vm_cfg["profile"] in GetHost(host_obj).shared_passthru_vgpu_types():
            self.logger.debug(
                "vGPU profile {0} is available "
                "for VM {1} ".format(vm_cfg["profile"], vm_cfg["vm"])
            )
            if vm_cfg["profile"] == vm_status.existing_vgpu_profile():
                self.logger.error(
                    "vGPU profile {0} is already configured for VM {1}. "
                    "Skip.".format(vm_cfg["profile"], vm_cfg["vm"])
                )
            else:
                tasks.append(vm_update.add_vgpu(vm_cfg["profile"]))
        else:
            self.logger.error(
                "vGPU profile {0} is not available for VM {1}. Skip.".format(
                    vm_cfg["profile"], vm_cfg["vm"]
                )
            )
        if tasks:
            if not vm_status.is_memory_reser_full():
                self.logger.warning(
                    "Adding a PCI device or shared PCI device "
                    "in passthrough mode needs to reserve memory. "
                    "Reserving memory."
                )
                tasks.append(vm_update.memory_reservation(reser=1))
            else:
                self.logger.debug("Good. Memory is already reserved.")
        return tasks

    def _get_remove_vgpu_tasks(self, vm_cfg):
        """
        Remove a vGPU profile for a VM and get Tasks

        Args:
            vm_cfg (dict): a dict contains VM config info

        Returns:
            list: a list of Tasks
        """
        tasks = []
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        vm_status = GetVM(vm_obj)
        vm_update = ConfigVM(vm_obj)

        Check().check_kv(vm_cfg, "profile", required=True)
        if vm_cfg["profile"] == vm_status.existing_vgpu_profile():
            self.logger.info(
                "vGPU {0} is to be removed "
                "from VM {1}".format(vm_cfg["profile"], vm_cfg["vm"])
            )
            tasks.append(vm_update.remove_vgpu(vm_cfg["profile"]))
        else:
            self.logger.error(
                "Couldn't find vgpu {0} on VM {1}. Skip.".format(
                    vm_cfg["profile"], vm_cfg["vm"]
                )
            )
        return tasks

    #~~~~~~~~~~~~~~~~~~~~~~~ vGPU END ~~~~~~~~~~~~~~~~~~~~~~~~#

    #~~~~~~~~~~~~~~~~~~~~~~ PVRDMA ~~~~~~~~~~~~~~~~~~~~~~~#
    def pvrdma_cli(self):
        """
        Add/Remove PVRDMA device for VM(s)

        Returns:
            None
        """
        vm_cfgs = self._extract_file(self.cfg)

        if self.cfg["add"]:
            tasks = []
            for vm_cfg in vm_cfgs:
                tasks.extend(self._get_add_pvrdma_tasks(vm_cfg))
            if tasks:
                GetWait().wait_for_tasks(tasks, task_name="Add PVRDMA device(s)")
        if self.cfg["remove"]:
            tasks = []
            for vm_cfg in vm_cfgs:
                tasks.append(self._get_remove_pvrdma_tasks(vm_cfg))
            if tasks:
                GetWait().wait_for_tasks(tasks, task_name="Remove PVRDMA device(s)")

    def _pvrdma_cluster(self, vm_cfgs, *keys):
        """
        Add/Remove PVRDMA device for VM(s) (defined in cluster conf file)

        Args:
            vm_cfgs (list): a list of dicts contains VM config info
            *keys: a keyword array that can trigger this configuration

        Returns:
            None
        """
        tasks = []

        for vm_cfg in vm_cfgs:
            if all(k in vm_cfg for k in keys):
                tasks.extend(self._get_add_pvrdma_tasks(vm_cfg))
        if tasks:
            GetWait().wait_for_tasks(tasks, task_name="Add PVRDMA device(s)")

    def _get_add_pvrdma_tasks(self, vm_cfg):
        """
        Add PVRDMA device(s) for a VM and get Task

        Args:
            vm_cfg (dict): a dict contains VM config info

        Returns:
            list: a list of Tasks
        """
        tasks = []
        Check().check_kv(vm_cfg, "dvs_name", required=True)
        dvs_name = vm_cfg["dvs_name"]
        dvs_obj = self.objs.get_dvs(dvs_name)
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        vm_update = ConfigVM(vm_obj)
        vm_status = GetVM(vm_obj)
        Check().check_kv(vm_cfg, "pvrdma_port_group", required=True)
        pg = vm_cfg["pvrdma_port_group"]
        pg_obj = self.objs.get_network(pg)
        self.logger.info("Found port group {0}".format(pg))
        if pg in vm_status.network_names():
            self.logger.error(
                "Port group {0} already exists on VM {1}. "
                "Skipping".format(pg, vm_obj.name)
            )
        else:
            tasks.append(vm_update.add_pvrdma(dvs_obj, pg_obj))
        if tasks:
            if not vm_status.is_memory_reser_full():
                self.logger.warning(
                    "Add a PVRDMA device needs to reserve memory. " "Reserving memory."
                )
                tasks.append(vm_update.memory_reservation(reser=1))
            else:
                self.logger.debug("Good. Memory is already reserved.")
        return tasks

    def _get_remove_pvrdma_tasks(self, vm_cfg):
        """
        Remove PVRDMA device from a VM and get Task

        Args:
            vm_cfg (dict): a dict contains vm config info

        Returns:
            Task
        """
        vm_obj = self.objs.get_vm(vm_cfg["vm"])
        Check().check_kv(vm_cfg, "pvrdma_port_group", required=True)
        pg = vm_cfg["pvrdma_port_group"]
        pg_obj = GetVM(vm_obj).network_obj(
            network_name=pg, device_type=vim.VirtualVmxnet3Vrdma
        )
        if pg_obj:
            self.logger.debug("Found port group {0} for VM {1}".format(pg, vm_obj.name))
            task = ConfigVM(vm_obj).remove_network_adapter(pg_obj)
            return task
        else:
            self.logger.error(
                "Couldn't find port group {0} "
                "on VM {1} to remove".format(pg, vm_obj.name)
            )
            return None

    #~~~~~~~~~~~~~~~~~~~~ PVRDMA END ~~~~~~~~~~~~~~~~~~~#

# ================ "Operations to add various devices on one VM" End ==================#

# ================ "Operations configured on host(s)" =================================#

    #~~~~~~~~~~~~~~~~~~~~~~~~ SVS ~~~~~~~~~~~~~~~~~~~~~~~~~~#

    def svs_cli(self):
        """
        Create a standard virtual switch

        Returns:
            None
        """
        if self.cfg["create"]:
            self._create_svs(self.cfg)

        if self.cfg["destroy"]:
            self._destroy_svs(self.cfg)

    def _create_svs(self, svs_cfg):
        """
        create a standard virtual switch. Note that the API for
        adding/destroying svs doesn't return Task to track

        Args:
            svs_cfg (dict): a dict contains svs config info

        Returns:
            None
        """
        Check().check_kv(svs_cfg, "name", required=True)
        Check().check_kv(svs_cfg, "pnic", required=True)
        Check().check_kv(svs_cfg, "host", required=True)
        svs = svs_cfg["name"]
        pnic = svs_cfg["pnic"]
        svs_hosts = []
        if isinstance(svs_cfg["host"], str):
            svs_hosts.append(svs_cfg["host"])
        elif isinstance(svs_cfg["host"], list):
            svs_hosts = svs_cfg["host"]
        else:
            pass
        for svs_host in svs_hosts:
            host_obj = self.objs.get_host(svs_host)
            host_update = ConfigHost(host_obj)
            try:
                host_update.create_svs(svs_name=svs, vmnic=pnic, mtu=svs_cfg.get("mtu"))
                self.logger.info(
                    "Creating standard virtual switch {0} " "is successful.".format(svs)
                )
            except vmodl.MethodFault as error:
                self.logger.error("Caught vmodl fault: " + error.msg)
            if Check().check_kv(svs_cfg, "port_group"):
                try:
                    host_update.create_pg_in_svs(
                        svs_name=svs, pg_name=svs_cfg["port_group"]
                    )
                    self.logger.info(
                        "Creating port group {0} "
                        "within virtual switch {1} is "
                        "successful.".format(svs_cfg["port_group"], svs)
                    )
                except vmodl.MethodFault as error:
                    self.logger.error("Caught vmodl fault: " + error.msg)

    def _destroy_svs(self, svs_cfg):
        """
        destroy a standard virtual switch. Note that the API for
        adding/destroying svs doesn't return Task to track

        Args:
            svs_cfg (dict): a dict contains svs config info

        Returns:
            None
        """
        Check().check_kv(svs_cfg, "host", required=True)
        Check().check_kv(svs_cfg, "name", required=True)
        svs_hosts = []
        if isinstance(svs_cfg["host"], str):
            svs_hosts.append(svs_cfg["host"])
        elif isinstance(svs_cfg["host"], list):
            svs_hosts = svs_cfg["host"]
        else:
            pass
        svs_name = svs_cfg["name"]
        for svs_host in svs_hosts:
            host_obj = self.objs.get_host(svs_host)
            host_update = ConfigHost(host_obj)
            # destroy port group within this svs first
            if Check().check_kv(svs_cfg, "port_group"):
                pg_name = svs_cfg["port_group"]
                try:
                    host_update.destroy_pg(pg_name)
                    self.logger.info(
                        "Destroying port group {0} "
                        "is successful.".format(svs_cfg["port_group"])
                    )
                except vmodl.MethodFault as error:
                    self.logger.error("Caught vmodl fault : " + error.msg)
            try:
                host_update.destroy_svs(svs_name)
                self.logger.info(
                    "Destroying virtual switch {0} is " "successful.".format(svs_name)
                )
            except vmodl.MethodFault as error:
                self.logger.error("Caught vmodl fault : " + error.msg)

    #~~~~~~~~~~~~~~~~~~~~~~~~ SVS END ~~~~~~~~~~~~~~~~~~~~~~#

    #~~~~~~~~~~~~~~~~~~~~~~~~ DVS ~~~~~~~~~~~~~~~~~~~~~~~~~~#
    def dvs_cli(self):
        """
        Create a distributed virtual switch

        Returns:
            None
        """
        if self.cfg["create"]:
            self._create_dvs(self.cfg)
        if self.cfg["destroy"]:
            self._destroy_dvs(self.cfg)

    def _create_dvs(self, dvs_cfg):
        """

        Args:
            dvs_cfg (dict): a dict contains dvs config info

        Returns:
            None
        """
        self.logger.info("Checking DVS arguments...")
        Check().check_kv(dvs_cfg, "name", required=True)
        Check().check_kv(dvs_cfg, "datacenter", required=True)
        Check().check_kv(dvs_cfg, "host", required=True)
        Check().check_kv(dvs_cfg, "pnic", required=True)
        self.logger.info("DVS arguments checking is completed")
        dvs_name = dvs_cfg["name"]
        pnics = []
        dvs_hosts = []
        if isinstance(dvs_cfg["host"], str):
            dvs_hosts.append(dvs_cfg["host"])
        elif isinstance(dvs_cfg["host"], list):
            dvs_hosts = dvs_cfg["host"]
        else:
            pass
        if isinstance(dvs_cfg["pnic"], str):
            pnics.append(dvs_cfg["pnic"])
        elif isinstance(dvs_cfg["pnic"], list):
            pnics.extend(dvs_cfg["pnic"])
        else:
            pass
        host_vmnics = {}
        datacenter_obj = self.objs.get_datacenter(dvs_cfg["datacenter"])
        for dvs_host in dvs_hosts:
            host_obj = self.objs.get_host(dvs_host)
            host_vmnics[host_obj] = pnics
        task = ConfigDatacenter(datacenter_obj).create_dvs(
            host_vmnics, dvs_name, mtu=dvs_cfg.get("mtu")
        )
        GetWait().wait_for_tasks([task], task_name="Create distributed virtual switch")
        # create port group within this DVS
        if Check().check_kv(dvs_cfg, "port_group"):
            dvs_obj = self.objs.get_dvs(dvs_name)
            task = ConfigDVS(dvs_obj).create_pg_in_dvs(dvs_cfg["port_group"])
            GetWait().wait_for_tasks(
                [task], task_name="Create port group within this DVS"
            )

    def _destroy_dvs(self, dvs_cfg):
        """

        Args:
            dvs_cfg (dict): a dict contains dvs config info

        Returns:
            None
        """
        Check().check_kv(dvs_cfg, "name", required=True)
        dvs_obj = self.objs.get_dvs(dvs_cfg["name"])
        # remove port group within this DVS first
        if dvs_obj.portgroup:
            for pg_obj in dvs_obj.portgroup:
                if "DVUplinks" not in pg_obj.name:
                    self.logger.info(
                        "Remove port group: {0} within the "
                        "DVS: {1} first".format(pg_obj.name, dvs_obj.name)
                    )
                    task = pg_obj.Destroy_Task()
                    GetWait().wait_for_tasks([task], task_name="Destroy port group")
        task = ConfigDVS(dvs_obj).destroy_dvs()
        GetWait().wait_for_tasks([task], task_name="Destroy distributed virtual switch")

    #~~~~~~~~~~~~~~~~~~~~~~~ DVS END ~~~~~~~~~~~~~~~~~~~~~~~#

    #~~~~~~~~~~~~~~~~~~~~~ HOSTSRIOV ~~~~~~~~~~~~~~~~~~~~~~~#
    def modify_host_sriov_cli(self):
        hosts = []
        if "host" in self.cfg:
            hosts.append(self.cfg["host"])
        else:
            hosts.extend(
                [
                    host_cfg["host"]
                    for host_cfg in self._extract_file(self.cfg, file_keys=["host"])
                ]
            )

        for host in hosts:
            ConfigHost(self.objs.get_host(host)).modify_sriov(
                self.cfg["device"],
                num_virtual_functions=self.cfg.get("num_func"),
                enable_sriov=bool(self.cfg["on"]),
            )

    #~~~~~~~~~~~~~~~~~~~~~ HOSTSRIOV END ~~~~~~~~~~~~~~~~~~~#

    # ~~~~~~~~~~~~~~~~~~~~~ PASSTHRUHOST ~~~~~~~~~~~~~~~~~~~#
    def passthru_host_cli(self):
        hosts = []
        if "host" in self.cfg:
            hosts.append(self.cfg["host"])
        else:
            hosts.extend(
                [
                    host_cfg["host"]
                    for host_cfg in self._extract_file(self.cfg, file_keys=["host"])
                ]
            )

        for host in hosts:
            host_obj = self.objs.get_host(host)
            ConfigHost(host_obj).toggle_pci_device_availability(
                self.cfg["device"], bool(self.cfg["on"])
            )

    # ~~~~~~~~~~~~~~~~~~~~~ PASSTHRUHOST END ~~~~~~~~~~~~~~~#

    # ~~~~~~~~~~~~~~~~~~~~~~ POWER POLICY ~~~~~~~~~~~~~~~~~~#
    def power_policy_cli(self):
        hosts = []

        if "host" in self.cfg:
            hosts.append(self.cfg["host"])
        else:
            hosts.extend(
                [
                    host_cfg["host"]
                    for host_cfg in self._extract_file(self.cfg, file_keys=["host"])
                ]
            )

        for host in hosts:
            host_obj = self.objs.get_host(host)
            ConfigHost(host_obj).change_power_policy(self.cfg["policy"])

    # ~~~~~~~~~~~~~~~~~~~~~ POWER POLICY END ~~~~~~~~~~~~~~~#

# ================ "Operations configured on host(s)" End ==============================#

    #~~~~~~~~~~~~~~~~~~~~~~~ CLUSTER ~~~~~~~~~~~~~~~~~~~~~#
    def cluster(self):
        """
        Cluster creation/destroy based on the definition from cluster conf file

        Returns:
            None
        """
        file_read = Cluster(self.cfg["file"])
        svs_cfgs = file_read.read_svs_dvs_section(sec_def_key="_SVS_")
        dvs_cfgs = file_read.read_svs_dvs_section(sec_def_key="_DVS_")
        vm_cfgs = file_read.read_vm_section(sec_def_key="_VMS_")
        if self.cfg["debug"]:
            if svs_cfgs:
                for svs_cfg in svs_cfgs:
                    self.logger.debug("_SVS_ read in as \n {0}".format(svs_cfg))
            else:
                self.logger.debug("No _SVS_ config info read in.")
            if dvs_cfgs:
                for dvs_cfg in dvs_cfgs:
                    self.logger.debug("_DVS_ read in as \n {0}".format(dvs_cfg))
            else:
                self.logger.debug("No _DVS_ config info read in.")
            if vm_cfgs:
                for vm_cfg in vm_cfgs:
                    self.logger.debug("_VMS_ read in as \n {0}".format(vm_cfg))
            else:
                self.logger.debug("No _VMS_ config info read in.")
        if len(svs_cfgs) == 0 and len(dvs_cfgs) == 0 and len(vm_cfgs) == 0:
            self.logger.error(
                "Couldn't correctly read cluster configuration "
                "file. Please check the format."
            )
            raise SystemExit
        if self.cfg["create"]:
            if svs_cfgs:
                self._create_cluster_svs(svs_cfgs)
            if dvs_cfgs:
                self._create_cluster_dvs(dvs_cfgs)
            if vm_cfgs:
                self._create_cluster_vms(vm_cfgs)
        if self.cfg["destroy"]:
            if vm_cfgs:
                self._destroy_cluster_vms(vm_cfgs)
            if svs_cfgs:
                self._destroy_cluster_svs(svs_cfgs)
            if dvs_cfgs:
                self._destroy_cluster_dvs(dvs_cfgs)

    def _create_cluster_svs(self, switch_cfgs):
        """

        Args:
            switch_cfgs (list): a list of dicts contain switch config info
                            which is extracted from cluster file

        Returns:
            None
        """
        for switch in switch_cfgs:
            self._create_svs(switch)

    def _create_cluster_dvs(self, switch_cfgs):
        """

        Args:
            switch_cfgs (list): a list of dicts contain switch config info which is extracted from cluster file

        Returns:
            None
        """
        for switch in switch_cfgs:
            self._create_dvs(switch)

    def _create_cluster_vms(self, vm_cfgs):
        """

        Args:
            vm_cfgs (list): a list of dicts contain VM config info which is extracted from cluster file

        Returns:
            None
        """
        self._clone_cluster(vm_cfgs, "template")
        self._cpu_shares_cluster(vm_cfgs, "cpu_shares")
        self._memory_shares_cluster(vm_cfgs, "memory_shares")
        self._cpumem_cluster(vm_cfgs, "cores_per_socket")
        self._cpumem_reser_cluster(vm_cfgs, "cpu_reservation", "memory_reservation")
        self._network_cluster(vm_cfgs, "port_group")
        self._network_cfg_cluster(vm_cfgs, "ip", "is_dhcp")
        self._latency_cluster(vm_cfgs, "latency")
        self._passthru_cluster(vm_cfgs, "device")
        self._vgpu_cluster(vm_cfgs, "vgpu")
        self._sriov_cluster(vm_cfgs, "sriov_port_group")
        self._pvrdma_cluster(vm_cfgs, "pvrdma_port_group")
        self._secure_boot_cluster(vm_cfgs, "secure_boot")
        self._power_cluster(vm_cfgs, "power")
        # execute post scripts with enforced order
        cluster_read = Cluster(self.cfg["file"])
        sorted_posts = cluster_read.collect_scripts(vm_cfgs)
        for post in sorted_posts:
            tasks = []
            for spec in post:
                usr, pwd, vm, scripts, _ = spec
                tasks.extend(self._get_post_procs(usr, pwd, vm, scripts))
            if tasks:
                proc_mng = self.content.guestOperationsManager.processManager
                GetWait().wait_for_procs(proc_mng, tasks)
        # get IP
        for vm_cfg in vm_cfgs:
            vm_obj = self.objs.get_vm(vm_cfg["vm"])
            GetVM(vm_obj).get_ip_addr()

    def _destroy_cluster_vms(self, vm_cfgs):
        """

        Args:
            vm_cfgs (list): a list of dicts contain VM config info
                            which is extracted from cluster file

        Returns:
            None
        """
        vms = [vm_cfg["vm"] for vm_cfg in vm_cfgs]
        if vms:
            confirm = input("[ACTION] Do you really want to destroy {0} ? ".format(vms))
            try:
                if bool(strtobool(confirm)):
                    tasks = self._get_destroy_tasks(vms)
                    if tasks:
                        GetWait().wait_for_tasks(tasks, task_name="Destroy VM")
                else:
                    self.logger.info("Not destroying any VMs")
            except ValueError:
                raise SystemExit("Not a valid answer. Exit.")
        else:
            self.logger.info("No VMs specified to destroy")

    def _destroy_cluster_svs(self, switch_cfgs):
        """

        Args:
            switch_cfgs (list): a list of dicts contain switch config info
                            which is extracted from cluster file

        Returns:
            None
        """
        svs_cfgs = [
            switch_cfg for switch_cfg in switch_cfgs if switch_cfg["op"] == "svs"
        ]
        svs_for_del = [svs["name"] for svs in svs_cfgs]
        if svs_for_del:
            confirm = input(
                "[ACTION] Do you really want to destroy standard virtual "
                "switches {0} ? ".format(svs_for_del)
            )
            if strtobool(confirm) == 1:
                for cl_config in svs_cfgs:
                    self._destroy_svs(cl_config)
            else:
                self.logger.info("Not destroying any standard virtual switches")

    def _destroy_cluster_dvs(self, switch_cfgs):
        """

        Args:
            switch_cfgs (list): a list of dicts contain switch config info
                            which is extracted from cluster file

        Returns:
            None
        """
        dvs_cfgs = [
            switch_cfg for switch_cfg in switch_cfgs if switch_cfg["op"] == "dvs"
        ]
        dvs_for_del = [dvs["name"] for dvs in dvs_cfgs]
        if dvs_for_del:
            confirm = input(
                "[ACTION] Do you really want to destroy distributed virtual "
                "switches {0} ? ".format(dvs_for_del)
            )
            if strtobool(confirm) == 1:
                for cl_config in dvs_cfgs:
                    self._destroy_dvs(cl_config)
            else:
                self.logger.info("Not destroying any distributed virtual switches")

    #~~~~~~~~~~~~~~~~~~~~~~~ CLUSTER END ~~~~~~~~~~~~~~~~~~~~~~~~~~#

    #~~~~~~~~~~~~~~~~~~~~~~ GETVMCONFIG ~~~~~~~~~~~~~~~~~~~~~~~#
    def get_vm_config_cli(self) -> None:
        vm_cfgs = self._extract_file(self.cfg)
        for vm_cfg in vm_cfgs:
            self._print_vm_config(vm_cfg["vm"])

    #~~~~~~~~~~~~~~~~~~~~~ GETVMCONFIG END ~~~~~~~~~~~~~~~~~~~~~#

    #~~~~~~~~~~~~~~~~~~~~~ PRINT_VM_CONFIG ~~~~~~~~~~~~~~~~~~~~~#
    def _print_vm_config(self, vm_name: str) -> None:
        """
        This function prints the performance related settings of the vm using the vm name provided

        Args:
            vm_name: Name of the VM for which you want the performance related settings printed
        Returns:
            None
        """
        vm_object: vim.VirtualMachine = self.objs.get_vm(vm_name)
        vm = GetVM(vm_object)

        existing_pci_ids = vm.existing_pci_ids()
        # Get PCI devices attached to the current VM
        attached_direct_passthru_devices = []
        for passthru_device in vm.avail_pci_info():
            if passthru_device[2] in existing_pci_ids:
                device_name, vendor_name, device_id, system_id = passthru_device
                attached_direct_passthru_devices.append(
                    {
                        "Device Name": f"{vendor_name} - {device_name}",
                        "Device ID": device_id,
                    }
                )

        # Get SRIOV devices to the current VM
        attached_sriov_devices = []
        existing_sriov_ids = vm.existing_sriov_ids()

        for sriov_device in vm.avail_sriov_info():
            if sriov_device[4] in existing_sriov_ids:
                (
                    pnic,
                    virtual_function,
                    device_name,
                    vendor_name,
                    device_id,
                    system_id,
                ) = sriov_device
                attached_sriov_devices.append(
                    {
                        "PNIC": pnic,
                        "Virtual Function": virtual_function,
                        "Device Name": f"{vendor_name} - {device_name}",
                        "Device ID": device_id,
                    }
                )

        attached_pvrmda_devices = []

        for network_object in vm.device_objs_all():
            if isinstance(
                    network_object, vim.vm.device.VirtualSriovEthernetCard
            ) and hasattr(network_object, "sriovBacking"):
                for attached_sriov_device in attached_sriov_devices:
                    if (
                            attached_sriov_device["Device ID"]
                            == network_object.sriovBacking.physicalFunctionBacking.id
                    ):
                        attached_sriov_device.update(
                            {"Label": network_object.deviceInfo.label}
                        )
            if isinstance(network_object, vim.vm.device.VirtualVmxnet3Vrdma):
                attached_pvrmda_devices.append(
                    {
                        "Label": network_object.deviceInfo.label,
                    }
                )
            if isinstance(network_object, vim.vm.device.VirtualPCIPassthrough) and (
                    hasattr(network_object.backing, "id")
                    or hasattr(network_object.backing, "assignedId")
            ):
                backing_id = (
                    getattr(network_object.backing, "id")
                    if hasattr(network_object.backing, "id")
                    else getattr(network_object.backing, "assignedId")
                )
                for attached_direct_passthru_device in attached_direct_passthru_devices:
                    if attached_direct_passthru_device["Device ID"] == backing_id:
                        attached_direct_passthru_device.update(
                            {"Label": network_object.deviceInfo.label}
                        )

        vm_details = {
            "Name": vm.vm_name(),
            "vCPU": vm.cpu(),
            "CPU Cores Per Socket": vm.cores_per_socket(),
            "CPU Reservation": f"{vm.cpu_reser()} MHz",
            "CPU Limit": f"{0 if vm_object.config.cpuAllocation.limit == -1 else vm_object.config.cpuAllocation.limit} MHz",
            "Memory Size": f"{round(vm.memory() / 1024.0, 2)} GB",
            "Memory Reservation": f"{round(vm.memory_reser() / 1024.0, 2)} GB",
            "Memory Limit": f"{round((0 if vm_object.config.memoryAllocation.limit == -1 else vm_object.config.memoryAllocation.limit) / 1024.0, 2)} GB",
            "Latency Sensitivity": vm.latency(),
            "PCI Devices": {
                "Passthrough": attached_direct_passthru_devices,
                "SRIOV": attached_sriov_devices,
                "PVRDMA": attached_pvrmda_devices,
            },
        }
        print("-----------------------------------------")
        print(json.dumps(vm_details, indent=4))
        print("-----------------------------------------")

    #~~~~~~~~~~~~~~~~~~~~~ PRINT_VM_CONFIG End ~~~~~~~~~~~~~~~~~~#
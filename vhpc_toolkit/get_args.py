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
import argparse
import os
import sys

import distutils.util
import yaml

sys.tracebacklimit = None
CMD_KEY = "command"


def get_args():
    """
    leverage argparse -- Python parser for command-line options for
                             passing arguments

    Returns:
        ArgumentParser object: hold all necessary command line info to pass
    """

    from vhpc_toolkit.version import __version__

    main_parser = argparse.ArgumentParser(
        description="Configuring vHPC environment",
    )
    main_parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        default=False,
        help="print debug messages",
    )
    main_parser.add_argument(
        "--version",
        action="version",
        version="vhpc_toolkit version %s" % __version__,
    )
    subparsers = main_parser.add_subparsers(dest=CMD_KEY)

    get_vm_config_parser = subparsers.add_parser(
        "get_vm_config",
        help="View the performance metrics of the VM",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    get_vm_config_group1 = get_vm_config_parser.add_mutually_exclusive_group(
        required=True
    )

    get_vm_config_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM whose performance related settings should be fetched",
    )
    get_vm_config_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs,"
        " one per line, to perform the operation",
    )

    view_parser = subparsers.add_parser(
        "view",
        help="View the vCenter object names",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    view_parser.add_argument(
        "--networking",
        action="store_true",
        help="Basic view plus networking view (virtual switches and "
        "networking adapters)",
    )
    clone_parser = subparsers.add_parser(
        "clone",
        help="Clone VM(s) via Full Clone or Linked Clone",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    clone_group1 = clone_parser.add_mutually_exclusive_group(required=True)
    clone_group2 = clone_parser.add_mutually_exclusive_group(required=False)
    clone_group1.add_argument(
        "--vm",
        required=False,
        action="store",
        default=None,
        type=str,
        help="Name of the cloned VM",
    )
    clone_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file with one clone destination specification "
        "(format: cloned_VM cluster host datastore) per line ",
    )
    clone_group2.add_argument(
        "--linked",
        action="store_true",
        help="Enable linked clone."
        "If linked clone is enabled, "
        "the dest datastore will be same "
        "as template's datastore. ",
    )
    clone_parser.add_argument(
        "--template",
        required=True,
        action="store",
        default=None,
        type=str,
        help="Name of the template VM to clone from ",
    )
    clone_parser.add_argument(
        "--datacenter",
        required=False,
        action="store",
        default=None,
        type=str,
        help="Name of the destination datacenter. \n"
        "If omitted, the first datacenter in the vCenter inventory"
        " will be used.",
    )
    clone_parser.add_argument(
        "--vm_folder",
        required=False,
        action="store",
        default=None,
        type=str,
        help="Name of the destination VM folder. \n"
        "If omitted, the first VM folder in the specified/default datacenter"
        " will be used.",
    )
    clone_parser.add_argument(
        "--cluster",
        required=False,
        action="store",
        default=None,
        type=str,
        help="Name of the destination cluster. \n"
        "If omitted, the first cluster in the specified/default datacenter"
        " will be used.",
    )
    clone_parser.add_argument(
        "--host",
        required=False,
        action="store",
        default=None,
        type=str,
        help="Name of the destination host. \n"
        "If omitted, the first host in the specified/default cluster"
        " will be used.",
    )
    clone_parser.add_argument(
        "--datastore",
        required=False,
        action="store",
        default=None,
        type=str,
        help="Name of the destination datastore. \n"
        "If omitted, the same datastore of the template will be used.",
    )
    clone_parser.add_argument(
        "--resource_pool",
        required=False,
        action="store",
        default=None,
        type=str,
        help="Name of the destination resource pool. \n"
        "If omitted, the first resource pool in the specified/default cluster"
        " will be used.",
    )
    clone_parser.add_argument(
        "--memory",
        required=False,
        action="store",
        default=None,
        type=float,
        help="Memory (in GB) for the cloned VM(s). \n"
        "If omitted, it will be the same as the template VM.",
    )
    clone_parser.add_argument(
        "--cpu",
        required=False,
        action="store",
        default=None,
        type=int,
        help="Number of CPUs for the cloned VM(s). \n"
        "If omitted, it will be the same as the template VM.",
    )
    destroy_parser = subparsers.add_parser(
        "destroy",
        help="Destroy VM(s)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    destroy_group = destroy_parser.add_mutually_exclusive_group(required=True)
    destroy_group.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM to destroy ",
    )
    destroy_group.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs," " one per line to destroy",
    )
    power_parser = subparsers.add_parser(
        "power",
        help="Power on/off VM(s)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    power_group1 = power_parser.add_mutually_exclusive_group(required=True)
    power_group2 = power_parser.add_mutually_exclusive_group(required=True)
    power_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to perform the power operation",
    )
    power_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs,"
        " one per line, to perform the power operation",
    )
    power_group2.add_argument("--on", action="store_true", help="Power on")
    power_group2.add_argument("--off", action="store_true", help="Power off")

    migrate_vm_parser = subparsers.add_parser(
        "migrate_vm",
        help="Migrate VM(s) to a different host",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    migrate_vm_group1 = migrate_vm_parser.add_mutually_exclusive_group(required=True)
    migrate_vm_group1.add_argument(
        "--vm",
        default=None,
        action="store",
        type=str,
        help="The VM to migrate to a different host",
    )
    migrate_vm_group1.add_argument(
        "--file",
        default=None,
        action="store",
        type=str,
        help="Name of the file containing a list of VMs,"
        " one per line, to perform the migrate operation",
    )
    migrate_vm_parser.add_argument(
        "--destination",
        default=None,
        action="store",
        type=str,
        required=True,
        help="The name of the destination host VM(s) should be migrated to",
    )

    power_policy_parser = subparsers.add_parser(
        "power_policy",
        help="Change the power policy for the host",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    power_policy_group1 = power_policy_parser.add_mutually_exclusive_group(
        required=True
    )
    power_policy_group1.add_argument(
        "--host",
        action="store",
        default=None,
        type=str,
        help="Name of the host whose power policy must be changed",
    )
    power_policy_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of host(s),"
        " one per line, to perform the change power policy operation",
    )
    power_policy_parser.add_argument(
        "--policy",
        action="store",
        type=int,
        help="The power policy to change it to. Specify the corresponding index for the power policy\n"
        "1 - High Performance, 2 - Balanced, 3- Low Power, 4 - Custom",
        required=True,
        choices=[1, 2, 3, 4],
    )

    secure_boot_parser = subparsers.add_parser(
        "secure_boot",
        help="Turn secure boot on/off VM(s)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    secure_boot_group1 = secure_boot_parser.add_mutually_exclusive_group(required=True)
    secure_boot_group2 = secure_boot_parser.add_mutually_exclusive_group(required=True)
    secure_boot_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to perform the secure boot operation",
    )
    secure_boot_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs,"
        " one per line, to perform the secure boot operation",
    )
    secure_boot_group2.add_argument("--on", action="store_true", help="Secure boot on")
    secure_boot_group2.add_argument(
        "--off", action="store_true", help="Secure boot off"
    )

    def affinity_array(string):
        affinity_list = []
        string = string.replace(" ", "")
        if not string:
            return []
        split_ranges = string.split(",")
        for affinity in split_ranges:
            # If the given affinity element is not a range, then parse it to integer
            if ":" not in affinity:
                if not affinity.isdigit():
                    raise argparse.ArgumentTypeError(
                        "Each affinity element must be a valid integer"
                    )
                else:
                    affinity_list.append(int(affinity))
            else:
                affinity_range = affinity.split(":")
                if len(affinity_range) not in {2, 3}:
                    raise argparse.ArgumentTypeError(
                        "Argument range must have valid number of elements"
                    )

                step_length = 1 if len(affinity_range) == 2 else int(affinity_range[2])

                if not all([affinity.isdigit() for affinity in affinity_range]):
                    raise argparse.ArgumentTypeError(
                        "Each affinity element must be a valid integer"
                    )
                elif int(affinity_range[1]) < int(affinity_range[0]):
                    raise argparse.ArgumentTypeError("Affinity range must be valid")
                # Convert the range to integer list
                affinity_list.extend(
                    list(
                        range(
                            int(affinity_range[0]),
                            int(affinity_range[1]) + 1,
                            step_length,
                        )
                    )
                )
        return affinity_list

    vm_affinity_parser = subparsers.add_parser(
        "vm_sched_affinity",
        help="Change VM scheduling affinity",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    vm_affinity_group1 = vm_affinity_parser.add_mutually_exclusive_group(required=True)
    vm_affinity_group2 = vm_affinity_parser.add_mutually_exclusive_group(required=True)

    vm_affinity_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to reconfigure scheduling affinity",
    )
    vm_affinity_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs, one per line,"
        " to reconfigure vm scheduling affinity",
    )

    vm_affinity_group2.add_argument(
        "--affinity",
        action="store",
        default=[],
        type=affinity_array,
        help="Use ':' for separating ranges and steps, and ',' to separate values.\n"
        "For example - 0, 2, 4:7, 8:12:2  would indicate processors 0, 2, 4, 5, 6, 7, 8, 10, 12",
    )
    vm_affinity_group2.add_argument(
        "--clear",
        action="store_true",
        help="Clear the scheduling affinity settings for the VM(s)",
    )

    numa_affinity_parser = subparsers.add_parser(
        "numa_affinity",
        help="Change NUMA node affinity",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    numa_affinity_group1 = numa_affinity_parser.add_mutually_exclusive_group(
        required=True
    )
    numa_affinity_group2 = numa_affinity_parser.add_mutually_exclusive_group(
        required=True
    )

    numa_affinity_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to change NUMA node affinity",
    )
    numa_affinity_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs, one per line,"
        " to reconfigure NUMA node affinity",
    )

    numa_affinity_group2.add_argument(
        "--affinity",
        action="store",
        default=[],
        type=affinity_array,
        help="Use ':' for separating ranges and steps, and ',' to separate values.\n"
        "For example - 0, 2, 4:7, 8:12:2  would indicate processors 0, 2, 4, 5, 6, 7, 8, 10, 12",
    )
    numa_affinity_group2.add_argument(
        "--clear",
        action="store_true",
        help="Clear the NUMA affinity settings for the VM(s)",
    )

    cpumem_parser = subparsers.add_parser(
        "cpumem",
        help="Reconfigure CPU/memory for VM(s)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    cpumem_group = cpumem_parser.add_mutually_exclusive_group(required=True)
    cpumem_group.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to reconfigure CPU/memory",
    )
    cpumem_group.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs, one per line,"
        " to reconfigure CPU/memory",
    )
    cpumem_parser.add_argument(
        "--memory",
        action="store",
        required=False,
        default=None,
        type=float,
        help="New memory (in GB) for VM(s)",
    )
    cpumem_parser.add_argument(
        "--cpu",
        action="store",
        required=False,
        default=None,
        type=int,
        help="New number of CPUs for VM(s)",
    )
    cpumem_parser.add_argument(
        "--cpu_shares",
        action="store",
        required=False,
        default=None,
        type=int,
        help="Shares of CPUs for VM(s)",
    )
    cpumem_parser.add_argument(
        "--cores_per_socket",
        action="store",
        required=False,
        default=None,
        type=int,
        help="Cores per socket for VM(s)",
    )
    cpumem_parser.add_argument(
        "--memory_shares",
        action="store",
        required=False,
        default=None,
        type=int,
        help="Shares of memory for VM(s)",
    )
    cpumem_parser.add_argument(
        "--memory_reservation",
        required=False,
        default=None,
        action="store",
        type=distutils.util.strtobool,
        help="Whether to reserve memory.\n"
        "Reserve memory: y, yes, t, true, or 1. \n"
        "Not reserve memory: n, no, f, false, or 0.\n",
    )
    cpumem_parser.add_argument(
        "--cpu_reservation",
        required=False,
        default=None,
        action="store",
        type=distutils.util.strtobool,
        help="Whether to reserve CPU. \n"
        "Reserve CPU: y, yes, t, true, or 1. \n"
        "Not reserve CPU: n, no, f, false, or 0.",
    )
    network_parser = subparsers.add_parser(
        "network",
        help="Add/Remove network adapter(s) for VM(s)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    network_config_parser = subparsers.add_parser(
        "network_cfg", help="Configure network(s) for VM(s)"
    )
    network_group1 = network_parser.add_mutually_exclusive_group(required=True)
    network_group2 = network_parser.add_mutually_exclusive_group(required=True)
    network_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to add network adapter",
    )
    network_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file with one vm name per line to add/remove "
        "network adapter",
    )
    network_group2.add_argument(
        "--add", action="store_true", help="Add a network adapter"
    )
    network_group2.add_argument(
        "--remove", action="store_true", help="Remove a network adapter"
    )
    network_parser.add_argument(
        "--port_group",
        action="store",
        required=True,
        nargs="+",
        type=str,
        help="Port group for the network adapter to add/remove",
    )
    network_config_parser.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        required=True,
        help="Name of the VM on which to configure network",
    )
    network_config_group = network_config_parser.add_mutually_exclusive_group(
        required=True
    )
    network_config_parser.add_argument(
        "--port_group",
        action="store",
        required=True,
        type=str,
        help="Number of the network adapter on which to configure network",
    )
    network_config_group.add_argument(
        "--is_dhcp", action="store_true", help="Use DHCP for this network"
    )
    network_config_group.add_argument(
        "--ip",
        action="store",
        default=None,
        type=str,
        help="Static IP address if not use DHCP",
    )
    network_config_parser.add_argument(
        "--netmask",
        action="store",
        default=None,
        required=True,
        type=str,
        help="Netmask",
    )
    network_config_parser.add_argument(
        "--gateway",
        action="store",
        default=None,
        required=True,
        type=str,
        help="Gateway",
    )
    network_config_parser.add_argument(
        "--dns",
        action="store",
        default=None,
        required=True,
        type=str,
        nargs="+",
        help="DNS server(s)",
    )
    network_config_parser.add_argument(
        "--domain",
        action="store",
        default=None,
        required=True,
        type=str,
        help="Domain name",
    )
    network_config_parser.add_argument(
        "--guest_hostname",
        action="store",
        default=None,
        required=False,
        type=str,
        help="Hostname of Guest OS. If omitted,"
        " VM name will be used as guest hostname",
    )
    post_parser = subparsers.add_parser(
        "post",
        help="Execute post script(s) in guest OS",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    post_group = post_parser.add_mutually_exclusive_group(required=True)
    post_group.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to execute post script(s)",
    )
    post_group.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs, one per line,"
        " to execute post script(s)",
    )
    post_parser.add_argument(
        "--script",
        action="store",
        required=True,
        nargs="+",
        type=str,
        default=None,
        help="Local post script(s) to be executed in guest OS",
    )
    post_parser.add_argument(
        "--guest_username",
        action="store",
        required=False,
        type=str,
        default="root",
        help="Guest OS username (default: %(default)s)",
    )
    post_parser.add_argument(
        "--guest_password",
        action="store",
        type=str,
        required=False,
        default=None,
        help="Guest OS password. If omitted, it will be prompted.",
    )
    post_parser.add_argument(
        "--wait",
        action="store_true",
        required=False,
        default=False,
        help="Wait for the script execution finish",
    )
    passthru_parser = subparsers.add_parser(
        "passthru",
        help="Add/Remove (large) PCI device(s) in Passthrough mode",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    passthru_group1 = passthru_parser.add_mutually_exclusive_group(required=True)
    passthru_group2 = passthru_parser.add_mutually_exclusive_group(required=False)
    passthru_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to perform the passthrough operation",
    )
    passthru_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs, "
        "one per line, to perform the passthrough operation",
    )
    passthru_parser.add_argument(
        "--query",
        action="store_true",
        help="Print available passthrough device(s) information for the VM(s)",
    )
    passthru_group2.add_argument(
        "--remove", action="store_true", help="Remove device(s)"
    )
    passthru_group2.add_argument("--add", action="store_true", help="Add device(s)")
    passthru_parser.add_argument(
        "--device",
        action="store",
        default=None,
        nargs="+",
        type=str,
        help="Device ID of the PCI device(s), for example: 0000:05:00.0",
    )
    passthru_parser.add_argument(
        "--mmio_size",
        action="store",
        required=False,
        type=int,
        default=256,
        help="64-bit MMIO size in GB for PCI device with large BARs. "
        "Default: %(default)s.",
    )
    passthru_parser.add_argument(
        "--dynamic",
        action="store_true",
        required=False,
        help="If this flag is added, PCI devices are added in dynamic direct i/o mode",
    )

    passthru_host_parser = subparsers.add_parser(
        "passthru_host",
        help="Enable/Disable PCI device(s) on host",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    passthru_host_group1 = passthru_host_parser.add_mutually_exclusive_group(
        required=True
    )
    passthru_host_group2 = passthru_host_parser.add_mutually_exclusive_group(
        required=True
    )
    passthru_host_group3 = passthru_host_parser.add_mutually_exclusive_group(
        required=True
    )
    passthru_host_group1.add_argument(
        "--host",
        action="store",
        default=None,
        type=str,
        help="Name of the host on which to enable/disable passthrough devices",
    )
    passthru_host_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of hosts, "
        "one per line, to enable/disable passthrough devices",
    )
    passthru_host_group2.add_argument(
        "--device",
        action="store",
        default=None,
        type=str,
        help="The ID of the PCI device to enable/disable on host",
    )
    passthru_host_group3.add_argument("--on", action="store_true", help="Enable device")
    passthru_host_group3.add_argument(
        "--off", action="store_true", help="Enable device"
    )

    sriov_parser = subparsers.add_parser(
        "sriov",
        help="Add/remove single root I/O virtualization (SR-IOV) device(s)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sriov_group1 = sriov_parser.add_mutually_exclusive_group(required=True)
    sriov_group2 = sriov_parser.add_mutually_exclusive_group(required=False)
    sriov_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to perform the SR-IOV operation",
    )
    sriov_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs, "
        "one per line, to perform the SR-IOV operation",
    )
    sriov_parser.add_argument(
        "--query",
        action="store_true",
        help="Print available SR-IOV device(s) information for the VM(s)",
    )
    sriov_group2.add_argument(
        "--add", action="store_true", help="Add SR-IOV device to VM(s)"
    )
    sriov_group2.add_argument(
        "--remove", action="store_true", help="Remove SR-IOV device from VM(s)"
    )
    sriov_parser.add_argument(
        "--sriov_port_group",
        action="store",
        type=str,
        help="Name of port group which could enable SR-IOV adapter type",
    )
    sriov_parser.add_argument(
        "--sriov_dvs_name",
        action="store",
        type=str,
        help="Name of distributed virtual switch which could enable SR-IOV",
    )

    sriov_parser.add_argument(
        "--pf",
        action="store",
        type=str,
        help="Name of physical function which backs up SR-IOV Passthrough",
    )

    sriov_parser.add_argument(
        "--allow_guest_mtu_change",
        action="store_true",
        help="Allow guest MTU change",
    )

    sriov_host_parser = subparsers.add_parser(
        "sriov_host",
        help="Modify SR-IOV configuration on host(s).\n"
        "This operation assumes that SR-IOV drivers have been installed on ESXi host",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sriov_host_group1 = sriov_host_parser.add_mutually_exclusive_group(required=True)
    sriov_host_group2 = sriov_host_parser.add_mutually_exclusive_group(required=True)
    sriov_host_group1.add_argument(
        "--host",
        action="store",
        default=None,
        type=str,
        help="Name of the host on which to perform the modify SR-IOV operation",
    )
    sriov_host_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of hosts, "
        "one per line, to perform the modify SR-IOV operation",
    )
    sriov_host_parser.add_argument(
        "--device",
        action="store",
        default=None,
        type=str,
        help="PCIe address of the Virtual Function (VF) of the SR-IOV device in format xxxx:xx:xx.x",
        required=True,
    )
    sriov_host_group2.add_argument(
        "--on", action="store_true", help="Turn on SR-IOV mode for device on host(s)"
    )
    sriov_host_group2.add_argument(
        "--off", action="store_true", help="Turn off SR-IOV mode for device on host(s)"
    )
    sriov_host_parser.add_argument(
        "--num_func",
        action="store",
        default=None,
        type=int,
        help="Number of virtual functions. This argument is ignored if used with --off flag. "
        "num_func must be equal or smaller than the VF enabled in firmware",
    )

    pvrdma_parser = subparsers.add_parser(
        "pvrdma",
        help="Add/Remove PVRDMA (Paravirtual RDMA) device(s)",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    pvrdma_group1 = pvrdma_parser.add_mutually_exclusive_group(required=True)
    pvrdma_group2 = pvrdma_parser.add_mutually_exclusive_group(required=True)
    pvrdma_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to perform the PVRDMA operation",
    )
    pvrdma_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs, "
        "one per line, to perform the PVRDMA operation",
    )
    pvrdma_group2.add_argument(
        "--add", action="store_true", help="Add PVRDMA device to VM(s)"
    )
    pvrdma_group2.add_argument(
        "--remove", action="store_true", help="Remove PVRDMA device from VM(s)"
    )
    pvrdma_parser.add_argument(
        "--pvrdma_port_group",
        action="store",
        type=str,
        required=True,
        help="Name of virtual network adapter which could enable PVRDMA",
    )
    pvrdma_parser.add_argument(
        "--dvs_name",
        action="store",
        type=str,
        required=True,
        help="Name of distributed virtual switch which could enable PVRDMA",
    )
    vgpu_parser = subparsers.add_parser(
        "vgpu",
        help="Add/Remove vGPU device in SharedPassthru mode",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    vgpu_group1 = vgpu_parser.add_mutually_exclusive_group(required=True)
    vgpu_group2 = vgpu_parser.add_mutually_exclusive_group(required=False)
    vgpu_group1.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to perform the vGPU operation",
    )
    vgpu_group1.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs, "
        "one per line, to perform the vGPU operation",
    )
    vgpu_parser.add_argument(
        "--query",
        action="store_true",
        help="Print available vGPU profiles information for the VM(s)",
    )
    vgpu_group2.add_argument(
        "--remove", action="store_true", help="Remove vGPU profile"
    )
    vgpu_group2.add_argument("--add", action="store_true", help="Add vGPU profile")
    vgpu_parser.add_argument(
        "--profile",
        action="store",
        default=None,
        type=str,
        help="Profile of the vGPU, for example: grid_p100-4q",
    )

    svs_parser = subparsers.add_parser(
        "svs",
        help="Create/destroy a standard virtual switch",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    svs_group1 = svs_parser.add_mutually_exclusive_group(required=True)
    svs_group1.add_argument(
        "--create", action="store_true", help="Create a standard virtual switch"
    )
    svs_group1.add_argument(
        "--destroy",
        action="store_true",
        help="Destroy a standard virtual switch",
    )
    svs_parser.add_argument(
        "--host",
        action="store",
        required=True,
        nargs="+",
        type=str,
        help="Name of the ESXi host on which to create a standard virtual " "switch",
    )
    svs_parser.add_argument(
        "--name",
        action="store",
        required=True,
        type=str,
        help="Name of the standard virtual switch to be created or destroyed",
    )
    svs_parser.add_argument(
        "--pnic",
        action="store",
        required=False,
        type=str,
        help="Physical NIC to be added into its standard virtual switch, "
        "e.g. vmnic0",
    )
    svs_parser.add_argument(
        "--port_group",
        action="store",
        type=str,
        help="Name of virtual port group to be created within "
        "this standard virtual switch",
    )
    svs_parser.add_argument(
        "--mtu",
        action="store",
        type=int,
        help="MTU to be set for the SVS. This argument is optional",
        required=False,
    )
    dvs_parser = subparsers.add_parser(
        "dvs",
        help="Create/destroy a distributed virtual switch",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    dvs_group1 = dvs_parser.add_mutually_exclusive_group(required=True)
    dvs_group1.add_argument(
        "--create",
        action="store_true",
        help="Create a distributed virtual switch",
    )
    dvs_group1.add_argument(
        "--destroy",
        action="store_true",
        help="Destroy a distributed virtual switch",
    )
    dvs_parser.add_argument(
        "--name",
        action="store",
        type=str,
        required=True,
        help="Name of distributed virtual switch to be created or destroyed",
    )
    dvs_parser.add_argument(
        "--datacenter",
        action="store",
        type=str,
        help="Name of the datacenter to create the distributed virtual "
        "switch. Note that all hosts need to be in the same datacenter.",
    )
    dvs_parser.add_argument(
        "--host",
        action="store",
        nargs="+",
        type=str,
        help="ESXi hosts to be added into this distributed virtual switch",
    )
    dvs_parser.add_argument(
        "--pnic",
        action="store",
        nargs="+",
        type=str,
        required=False,
        help="Physical NIC(s) on each host to be added into "
        "this distributed virtual switch, e.g. vmnic0 vmnic1",
    )
    dvs_parser.add_argument(
        "--port_group",
        action="store",
        type=str,
        required=False,
        help="Name of virtual port group to be created "
        "within this distributed virtual switch",
    )
    dvs_parser.add_argument(
        "--mtu",
        action="store",
        type=int,
        help="MTU to be set for the DVS. This argument is optional",
        required=False,
    )
    latency_parser = subparsers.add_parser(
        "latency",
        help="Configure/Check latency sensitivity",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    latency_group = latency_parser.add_mutually_exclusive_group(required=True)
    latency_group.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        help="Name of the VM on which to configure latency sensitivity",
    )
    latency_group.add_argument(
        "--file",
        action="store",
        default=None,
        type=str,
        help="Name of the file containing a list of VMs, "
        "one per line, to configure latency sensitivity",
    )
    latency_parser.add_argument(
        "--level",
        default=None,
        action="store",
        type=str,
        help="Set Latency Sensitivity level, available: high or normal",
    )
    latency_parser.add_argument(
        "--check", action="store_true", help="Check Latency Sensitivity level"
    )
    cluster_parser = subparsers.add_parser(
        "cluster",
        help="Create/Destroy vHPC cluster based on cluster configuration file",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    cluster_group = cluster_parser.add_mutually_exclusive_group(required=True)
    cluster_group.add_argument("--create", action="store_true", help="Create a cluster")
    cluster_group.add_argument(
        "--destroy", action="store_true", help="Destroy a cluster"
    )
    cluster_parser.add_argument(
        "--file",
        required=True,
        action="store",
        default=None,
        help="Name of the cluster configuration file",
    )
    return main_parser


def _find_vcenter_conf_file(file):
    """locate the vcenter conf file

    Args:
        file (str): vcenter conf file

    Returns:
        Full path of the vcenter conf file if located (str)

    """

    from os.path import expanduser

    home_conf_dir = expanduser("~") + "/vhpc_toolkit"
    home_conf_dir = os.path.abspath(home_conf_dir)
    home_conf_file = "%s/%s" % (home_conf_dir, file)
    default_conf_dir = "../config"
    default_conf_dir = os.path.abspath(default_conf_dir)
    default_conf_file = "%s/%s" % (default_conf_dir, file)
    if os.path.isfile(home_conf_file):
        conf_file = home_conf_file
    elif os.path.isfile(default_conf_file):
        conf_file = default_conf_file
    else:
        raise SystemExit(
            "Couldn't find %s under %s or "
            "%s" % (file, default_conf_dir, home_conf_dir)
        )
    return conf_file


def find_script_conf_file(file):
    """locate the cluster conf file

    Args:
        file (str): cluster conf file

    Returns:
        Full path of the conf file if located (str)

    """

    default_conf_dir = "%s/../examples/cluster-scripts" % os.path.dirname(
        os.path.realpath(__file__)
    )
    default_conf_file = "%s/%s" % (default_conf_dir, file)
    if os.path.isfile(file):
        conf_file = file
    elif os.path.isfile(default_conf_file):
        conf_file = default_conf_file
    else:
        raise SystemExit("Couldn't find script file %s" % file)
    return conf_file


def get_global_config(kwargs):
    """

    Args:
        kwargs: namespace of config parameters

    Returns:
        dict1, dict2: dict1 contains global config properties,
        dict2 contains vcenter credentials

    """

    global_config = {}
    for key, value in kwargs.items():
        if value is not None:
            global_config[key] = value

    vcenter_config = {}
    vcenter_file = _find_vcenter_conf_file("vCenter.conf")
    try:
        f = open(vcenter_file, "r")
        loader = yaml.safe_load(f)
        vcenter_config.update(loader)
        f.close()
    except OSError:
        raise SystemExit(
            "Unable to read {0} file under config folder".format(vcenter_file)
        )
    return global_config, check_vcenter_config(vcenter_config)


def check_vcenter_config(vcenter_config):
    """

    Args:
        vcenter_config: the vCenter config dictionary

    Returns:
        dict: vcenter_config dict after checking

    """

    from vhpc_toolkit.cluster import Check

    check = Check()
    check.check_kv(vcenter_config, "server", required=True)
    check.check_kv(vcenter_config, "username", required=True)
    if not check.check_kv(vcenter_config, "port"):
        vcenter_config["port"] = 443  # vCenter default port
    # It will be not convenient to prompt password.
    # Just leave this option in case people need it.
    if not check.check_kv(vcenter_config, "password"):
        print(
            "If you want to enable automation and skip being prompted "
            "for password for every operation, you can consider "
            "leveraging Vault and putting password key in vCenter.conf. "
            "Checking README.md Security Section for more details."
        )
        import getpass

        vcenter_config["password"] = getpass.getpass("vCenter password: ")
    return vcenter_config

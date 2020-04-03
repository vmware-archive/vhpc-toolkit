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
from distutils.util import strtobool

sys.tracebacklimit = None
CMD_KEY = "command"


def get_main_parser():
    """ leverage argparse -- Python parser for command-line options for
							 passing arguments

	Returns:
		ArgumentParser object: hold all necessary command line info to pass

	"""

    from vhpc_toolkit.version import __version__

    main_parser = argparse.ArgumentParser(description="Configuring vHPC environment")
    main_parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        default=False,
        help="print debug messages",
    )
    main_parser.add_argument(
        "--version", action="version", version="vhpc_toolkit version %s" % __version__,
    )
    return main_parser


def get_view_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    view_parser = subparser.add_parser(
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
    return view_parser


def get_clone_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    clone_parser = subparser.add_parser(
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
    return clone_parser


def get_destroy_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    destroy_parser = subparser.add_parser(
        "destroy", help="Destroy VM(s)", formatter_class=argparse.RawTextHelpFormatter,
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
    return destroy_parser


def get_power_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    power_parser = subparser.add_parser(
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
    return power_parser


def get_cpumem_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    cpumem_parser = subparser.add_parser(
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
        type=strtobool,
        help="Whether to reserve memory.\n"
        "Reserve memory: y, yes, t, true, or 1. \n"
        "Not reserve memory: n, no, f, false, or 0.\n",
    )
    cpumem_parser.add_argument(
        "--cpu_reservation",
        required=False,
        default=None,
        action="store",
        type=strtobool,
        help="Whether to reserve CPU. \n"
        "Reserve CPU: y, yes, t, true, or 1. \n"
        "Not reserve CPU: n, no, f, false, or 0.",
    )
    return cpumem_parser


def get_network_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    network_parser = subparser.add_parser(
        "network",
        help="Add/Remove network adapter(s) for VM(s)",
        formatter_class=argparse.RawTextHelpFormatter,
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
        default="VM Network",
        # nargs="+",
        required=False,
        type=str,
        help="Port group for the network adapter to add/remove",
    )
    return network_parser


def get_network_cfg_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    network_cfg_parser = subparser.add_parser(
        "network_cfg", help="Configure network(s) for VM(s)"
    )
    network_cfg_parser.add_argument(
        "--vm",
        action="store",
        default=None,
        type=str,
        required=True,
        help="Name of the VM on which to configure network",
    )
    network_config_group = network_cfg_parser.add_mutually_exclusive_group(
        required=True
    )
    network_cfg_parser.add_argument(
        "--port_group",
        action="store",
        default="VM Network",
        required=False,
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
    network_cfg_parser.add_argument(
        "--netmask",
        action="store",
        default=None,
        required=True,
        type=str,
        help="Netmask",
    )
    network_cfg_parser.add_argument(
        "--gateway",
        action="store",
        default=None,
        required=True,
        type=str,
        help="Gateway",
    )
    network_cfg_parser.add_argument(
        "--dns",
        action="store",
        default=None,
        required=True,
        type=str,
        nargs="+",
        help="DNS server(s)",
    )
    network_cfg_parser.add_argument(
        "--domain",
        action="store",
        default=None,
        required=True,
        type=str,
        help="Domain name",
    )
    network_cfg_parser.add_argument(
        "--guest_hostname",
        action="store",
        default=None,
        required=False,
        type=str,
        help="Hostname of Guest OS. If omitted,"
        " VM name will be used as guest hostname",
    )
    return network_cfg_parser


def get_post_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    post_parser = subparser.add_parser(
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
    return post_parser


def get_passthru_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    passthru_parser = subparser.add_parser(
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
    return passthru_parser


def get_sriov_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    sriov_parser = subparser.add_parser(
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
        "--pf",
        action="store",
        type=str,
        help="Name of physical function which backs up SR-IOV Passthrough",
    )
    return sriov_parser


def get_pvrdma_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    pvrdma_parser = subparser.add_parser(
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
        help="Name of distributed virtual switch which could enable PVRDMA",
    )
    return pvrdma_parser


def get_vgpu_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    vgpu_parser = subparser.add_parser(
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
    return vgpu_parser


def get_svs_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    svs_parser = subparser.add_parser(
        "svs",
        help="Create/destroy a standard virtual switch",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    svs_group1 = svs_parser.add_mutually_exclusive_group(required=True)
    svs_group1.add_argument(
        "--create", action="store_true", help="Create a standard virtual switch"
    )
    svs_group1.add_argument(
        "--destroy", action="store_true", help="Destroy a standard virtual switch",
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
    return svs_parser


def get_dvs_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    dvs_parser = subparser.add_parser(
        "dvs",
        help="Create/destroy a distributed virtual switch",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    dvs_group1 = dvs_parser.add_mutually_exclusive_group(required=True)
    dvs_group1.add_argument(
        "--create", action="store_true", help="Create a distributed virtual switch",
    )
    dvs_group1.add_argument(
        "--destroy", action="store_true", help="Destroy a distributed virtual switch",
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
    return dvs_parser


def get_latency_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    latency_parser = subparser.add_parser(
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
    return latency_parser


def get_cluster_parser():
    subparser = get_main_parser().add_subparsers(dest=CMD_KEY)
    cluster_parser = subparser.add_parser(
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
    return cluster_parser


def find_conf_file(file):
    """ locate the cluster conf file

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
        conf_file = os.path.abspath(file)
    elif os.path.isfile(default_conf_file):
        conf_file = os.path.abspath(default_conf_file)
    else:
        print("[ERROR] Couldn't find the file %s" % file)
        raise SystemExit
    return conf_file

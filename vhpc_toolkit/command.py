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
from vhpc_toolkit import get_args
from vhpc_toolkit.operations import Operations


CMD_KEY = "command"


def command():
    parser = get_args.get_args()
    args = parser.parse_args()
    kwargs = vars(args)
    ops = Operations(**kwargs)
    if CMD_KEY not in ops.cfg:
        print(parser.print_help())
        raise SystemExit(0)
    if ops.cfg[CMD_KEY] == "view":
        ops.view_cli()
    elif ops.cfg[CMD_KEY] == "clone":
        ops.clone_cli()
    elif ops.cfg[CMD_KEY] == "destroy":
        ops.destroy_cli()
    elif ops.cfg[CMD_KEY] == "power":
        ops.power_cli()
    elif ops.cfg[CMD_KEY] == "network":
        ops.network_cli()
    elif ops.cfg[CMD_KEY] == "network_cfg":
        ops.network_cfg_cli()
    elif ops.cfg[CMD_KEY] == "post":
        ops.post_cli()
    elif ops.cfg[CMD_KEY] == "passthru":
        ops.passthru_cli()
    elif ops.cfg[CMD_KEY] == "sriov":
        ops.sriov_cli()
    elif ops.cfg[CMD_KEY] == "vgpu":
        ops.vgpu_cli()
    elif ops.cfg[CMD_KEY] == "pvrdma":
        ops.pvrdma_cli()
    elif ops.cfg[CMD_KEY] == "svs":
        ops.svs_cli()
    elif ops.cfg[CMD_KEY] == "dvs":
        ops.dvs_cli()
    elif ops.cfg[CMD_KEY] == "cpumem":
        ops.cpumem_cli()
    elif ops.cfg[CMD_KEY] == "latency":
        ops.latency_cli()
    elif ops.cfg[CMD_KEY] == "cluster":
        ops.cluster()
    elif ops.cfg[CMD_KEY] == "get_vm_config":
        ops.get_vm_config_cli()
    elif ops.cfg[CMD_KEY] == "secure_boot":
        ops.secure_boot_cli()
    elif ops.cfg[CMD_KEY] == "vm_sched_affinity":
        ops.vm_scheduling_affinity_cli()
    elif ops.cfg[CMD_KEY] == "numa_affinity":
        ops.numa_affinity_cli()
    elif ops.cfg[CMD_KEY] == "power_policy":
        ops.power_policy_cli()
    elif ops.cfg[CMD_KEY] == "sriov_host":
        ops.modify_host_sriov_cli()
    elif ops.cfg[CMD_KEY] == "migrate_vm":
        ops.migrate_vm_cli()

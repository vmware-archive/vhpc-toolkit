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
import cmd

from vhpc_toolkit import connect
from vhpc_toolkit import get_args
from vhpc_toolkit.operations import Operations


class Shell(cmd.Cmd):
    intro = (
        "Welcome to the vHPC Toolkit Shell. "
        "Type help or ? to list commands. Type exit to exit the shell.\n"
    )
    prompt = "vhpc_toolkit> "

    def __init__(self):
        super().__init__()
        main_args = get_args.get_main_parser().parse_args()
        self.main_kargs = vars(main_args)

        vcenter_cfg = connect.get_vcenter_config()

        # connect vCenter
        if vcenter_cfg["validate_certs"]:
            if not vcenter_cfg["certfile"]:
                print("Please provide certificate file.")
                exit(1)
            self.content = connect.connect(
                host=vcenter_cfg["server"],
                username=vcenter_cfg["username"],
                password=vcenter_cfg["password"],
                port=int(vcenter_cfg["port"]),
                keyfile=vcenter_cfg["keyfile"],
                certfile=vcenter_cfg["certfile"],
            )
        else:
            self.content = connect.connect(
                host=vcenter_cfg["server"],
                username=vcenter_cfg["username"],
                password=vcenter_cfg["password"],
                port=int(vcenter_cfg["port"]),
            )
        # delete credentials after connection
        del vcenter_cfg

    @staticmethod
    def emptyline():
        return

    @staticmethod
    def help_view():
        get_args.get_view_parser().print_help()

    @staticmethod
    def help_clone():
        get_args.get_clone_parser().print_help()

    @staticmethod
    def help_destroy():
        get_args.get_destroy_parser().print_help()

    @staticmethod
    def help_power():
        get_args.get_power_parser().print_help()

    @staticmethod
    def help_network():
        get_args.get_network_parser().print_help()

    @staticmethod
    def help_network_cfg():
        get_args.get_network_cfg_parser().print_help()

    @staticmethod
    def help_post():
        get_args.get_post_parser().print_help()

    @staticmethod
    def help_passthru():
        get_args.get_passthru_parser().print_help()

    @staticmethod
    def help_sriov():
        get_args.get_sriov_parser().print_help()

    @staticmethod
    def help_vgpu():
        get_args.get_vgpu_parser().print_help()

    @staticmethod
    def help_pvrdma():
        get_args.get_pvrdma_parser().print_help()

    @staticmethod
    def help_svs():
        get_args.get_svs_parser().print_help()

    @staticmethod
    def help_dvs():
        get_args.get_dvs_parser().print_help()

    @staticmethod
    def help_cpumem():
        get_args.get_cpumem_parser().print_help()

    @staticmethod
    def help_latency():
        get_args.get_latency_parser().print_help()

    @staticmethod
    def help_cluster():
        get_args.get_cluster_parser().print_help()

    def do_view(self, arg):
        try:
            ops = self.get_ops("view", arg)
            ops.view_cli()
        except SystemExit:
            return

    def do_clone(self, arg):
        try:
            ops = self.get_ops("clone", arg)
            ops.clone_cli()
        except SystemExit:
            return

    def do_destroy(self, arg):
        try:
            ops = self.get_ops("destroy", arg)
            ops.destroy_cli()
        except SystemExit:
            return

    def do_power(self, arg):
        try:
            ops = self.get_ops("power", arg)
            ops.power_cli()
        except SystemExit:
            return

    def do_network(self, arg):
        try:
            ops = self.get_ops("network", arg)
            ops.network_cli()
        except SystemExit:
            return

    def do_network_cfg(self, arg):
        try:
            ops = self.get_ops("network_cfg", arg)
            ops.network_cfg_cli()
        except SystemExit:
            return

    def do_passthru(self, arg):
        try:
            ops = self.get_ops("passthru", arg)
            ops.passthru_cli()
        except SystemExit:
            return

    def do_sriov(self, arg):
        try:
            ops = self.get_ops("sriov", arg)
            ops.sriov_cli()
        except SystemExit:
            return

    def do_pvrdma(self, arg):
        try:
            ops = self.get_ops("pvrdma", arg)
            ops.pvrdma_cli()
        except SystemExit:
            return

    def do_post(self, arg):
        try:
            ops = self.get_ops("post", arg)
            ops.post_cli()
        except SystemExit:
            return

    def do_vgpu(self, arg):
        try:
            ops = self.get_ops("vgpu", arg)
            ops.vgpu_cli()
        except SystemExit:
            return

    def do_svs(self, arg):
        try:
            ops = self.get_ops("svs", arg)
            ops.vgpu_cli()
        except SystemExit:
            return

    def do_dvs(self, arg):
        try:
            ops = self.get_ops("dvs", arg)
            ops.dvs_cli()
        except SystemExit:
            return

    def do_cpumem(self, arg):
        try:
            ops = self.get_ops("cpumem", arg)
            ops.cpumem_cli()
        except SystemExit:
            return

    def do_latency(self, arg):
        try:
            ops = self.get_ops("latency", arg)
            ops.latency_cli()
        except SystemExit:
            return

    def do_cluster(self, arg):
        try:
            ops = self.get_ops("cluster", arg)
            ops.cluster()
        except SystemExit:
            return

    def get_ops(self, method, arg):
        args = getattr(get_args, "get_" + method + "_parser")().parse_args(arg.split())
        kwargs = vars(args)
        kwargs = {**self.main_kargs, **kwargs}
        ops = Operations(self.content, **kwargs)
        return ops


class Exit(cmd.Cmd):
    @staticmethod
    def do_exit(s):
        return True

    @staticmethod
    def help_exit():
        print("Exit the interactive shell")


class Cmd(Shell, Exit):
    pass

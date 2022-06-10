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
from textwrap3 import TextWrapper


class View(object):
    """
    a class for wrapped view cli output
    """

    def __init__(self, view_entity, cur_level):
        """

        Args:
            view_entity: the managed object for viewing, including
                          vim.Folder, vim.ComputeResource,
                           vim.DistributedVirtualPortgroup
            cur_level (int): the current level for indentation
        """

        self.view_entity = view_entity
        self.cur_level = cur_level

    @staticmethod
    def _view_wrapper(fill_content, indentation):
        """print out the wrapped output with TextWrapper

        Args:
                fill_content (str): the content for printing
                indentation (str): string that will be indented to
                                   the wrapped output

        """

        text_wrapper = TextWrapper(
            initial_indent=indentation, subsequent_indent=indentation
        )
        print(text_wrapper.fill(fill_content))

    def view_compute_resource(self):
        """view compute resources

        Returns:
                None

        """

        if isinstance(self.view_entity, vim.ComputeResource):
            self._view_wrapper(
                "|-+:%s" % self.view_entity.name, self.cur_level * 2 * " "
            )
            for host in self.view_entity.host:
                self._view_wrapper(
                    "|-+:%s [Host][%s]" % (host.name, host.runtime.connectionState),
                    (self.cur_level * 2 + 2) * " ",
                )
                for vm in host.vm:
                    self._view_wrapper(
                        "|-:%s [VM]" % vm.name, (self.cur_level * 2 + 4) * " "
                    )
        elif isinstance(self.view_entity, vim.Folder):
            self._view_wrapper(
                "|-+:%s" % self.view_entity.name, self.cur_level * 2 * " "
            )
            next_level = self.cur_level + 1
            for entity in self.view_entity.childEntity:
                View(entity, next_level).view_compute_resource()

    def view_network_resource(self):
        """view networking resources

        Returns:
                None

        """

        if isinstance(self.view_entity, vim.DistributedVirtualSwitch):
            self._view_wrapper(
                "|-+:%s [DVS]" % self.view_entity.name,
                self.cur_level * 2 * " ",
            )
            for pg in self.view_entity.portgroup:
                self._view_wrapper(
                    "|-:%s [Portgroup]" % pg.name,
                    (self.cur_level * 2 + 2) * " ",
                )
        elif isinstance(self.view_entity, vim.Network) and not isinstance(
            self.view_entity, vim.DistributedVirtualPortgroup
        ):
            self._view_wrapper(
                "|-:%s [Netowrk]" % self.view_entity.name, self.cur_level * 2 * " "
            )
        elif isinstance(self.view_entity, vim.Folder):
            self._view_wrapper(
                "|-+:%s [Folder]" % self.view_entity.name, self.cur_level * 2 * " "
            )
            next_level = self.cur_level + 1
            # print("Number of child %s" % len(self.view_entity.childEntity))
            for entity in self.view_entity.childEntity:
                View(entity, next_level).view_network_resource()

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
import configparser
import itertools
import re
from collections import OrderedDict
from operator import itemgetter

from distutils.util import strtobool
from texttable import Texttable

from vhpc_toolkit import get_args
from vhpc_toolkit import log


class Cluster(object):
    """
    Read cluster configuration file
    """

    def __init__(self, file):
        """

        Args:
            file (str): cluster configuration file

        """

        self.file = file
        self.logger = log.my_logger(name=self.__class__.__name__)
        self.cfg_parser = configparser.ConfigParser()
        # Adding next line to prevent parser from converting everything to lowercase
        self.cfg_parser.optionxform = str
        cluster_file = get_args.find_script_conf_file(self.file)
        try:
            self.cfg_parser.read(cluster_file)
        except Exception as e:
            self.logger.error(e.__doc__)
            raise SystemExit

    @staticmethod
    def _scatter_mapping(list1, list2):
        """maps list1 to list2 in a scatter way

        Args:
            list1 (list)
            list2 (list)

        Returns:
            list

        """

        if len(list1) < len(list2):
            raise RangeMappingError
        return [i for i, _ in zip(itertools.cycle(list2), list1)]

    @staticmethod
    def _bunch_mapping(list1, list2):
        """maps list1 to list2 in a bunch way


        Args:
            list1 (list)
            list2 (list)

        Returns:
            list

        """

        if len(list1) < len(list2):
            raise RangeMappingError
        iters = int(len(list1) / len(list2))
        return [
            j
            for j in itertools.chain.from_iterable(
                itertools.repeat(i, iters) for i in list2
            )
        ]

    def read_svs_dvs_section(self, sec_def_key):
        """read _SVS_ section in the cluster configuration file

        Returns:
            list: a list of dicts, each dict contains one standard virtual
                  switch creation/destroy info

        """

        cfgs = []
        try:
            # for every row in the _SVS_ or _DVS_ section:
            for switch_name in self.cfg_parser.options(sec_def_key):
                cfg = {}
                # add 'op' key for driving operation
                cfg["op"] = sec_def_key.replace("_", "").lower()
                cfg["name"] = switch_name
                op_defs = self.cfg_parser.get(sec_def_key, switch_name)
                op_defs = self._remove_space(op_defs)
                # for each property definition
                for op_def in op_defs.split():
                    # if the property is a predefined section
                    if op_def in self.cfg_parser.sections():
                        # get every property in that predefined section
                        for k in self.cfg_parser.options(op_def):
                            v = self.cfg_parser.get(op_def, k)
                            # the value could be empty. If empty, ignore
                            if v:
                                self._add_item_svs_dvs(cfg, k, v)
                                # cfg = self._add_item_svs_dvs(cfg, k, v)
                    # if the property is defined as key:value pair
                    elif ":" in op_def:
                        k = op_def.split(":", maxsplit=1)[0]
                        v = op_def.split(":", maxsplit=1)[1]
                        if v:
                            self._add_item_svs_dvs(cfg, k, v)
                    else:
                        raise UnknownKeyError(op_def)
                # unfold range
                self._unfold_range_svs_dvs(cfg)
                cfgs.append(dict(cfg))
            return cfgs
        except UnknownKeyError as e:
            e.log()
            raise SystemExit
        except configparser.NoSectionError:
            # It's fine without _SVS_ or _DVS_ section
            return []
        except RangeMappingError as e:
            e.log()
            raise SystemExit

    def _unfold_range_svs_dvs(self, cfg):
        """Pass the cfg dict and scan the range key(s).
            If range is defined, unfold range,
            e.g. {key: value{1:10}} will become {key: [value1, value2,
            .. value10]}
            For svs or dvs, currently only 'host' key is supported for range
            definition

        Args:
            cfg (dict): the cfg dict return by initial reading

        """

        range_key = "host"
        if not Check().check_kv(cfg, range_key):
            return
        scatter_unfold, scatter_mark = self._range_unfold_scatter(
            range_key, cfg[range_key]
        )
        bunch_unfold, bunch_mark = self._range_unfold_bunch(range_key, cfg[range_key])
        if scatter_mark:
            cfg[range_key] = scatter_unfold[range_key]
        # svs and dvs don't support bunch mapping for the range key
        elif bunch_mark:
            self.logger.error(
                "For cluster level operation, the {0} "
                "key doesn't support bunch "
                "mapping".format(range_key)
            )
            raise RangeMappingError

    def read_vm_section(self, sec_def_key):
        """read _VM_ section in the cluster configuration file

        Returns:
            list: a list of dicts, each dict contains one VM creation/destroy
                  info

        """

        cfgs = []
        try:
            # for each row under _VMS_ section
            for vm_name in self.cfg_parser.options(sec_def_key):
                cfg = {}
                op_defs = self.cfg_parser.get(sec_def_key, vm_name)
                op_defs = self._remove_space(op_defs)
                # if the first separation contains '{', that means the VM
                # names are defined in range way. Need to get
                # full VM names by completing the other half of separation
                if re.findall("{", vm_name):
                    vm_name = vm_name + ":" + op_defs.split(":", 1)[0]
                    op_defs = op_defs.split(":", 1)[1]
                cfg["vm"] = vm_name
                # for each property definition
                for op_def in op_defs.split():
                    # if the property definition is a predefined section
                    if op_def in self.cfg_parser.sections():
                        # get each property in that predefined section
                        for k in self.cfg_parser.options(op_def):
                            v = self.cfg_parser.get(op_def, k)
                            # sometimes, the value could be empty.
                            # If empty, ignore it.
                            if v:
                                cfg = self._add_item_vm(cfg, k, v)
                    # if defined in a key:value pair way
                    elif ":" in op_def:
                        # get the key:value
                        k = op_def.split(":", maxsplit=1)[0]
                        v = op_def.split(":", maxsplit=1)[1]
                        if v:
                            # add the key: value pair into the config dict
                            cfg = self._add_item_vm(cfg, k, v)
                    else:
                        raise UnknownKeyError(op_def)
                # unfold ranges
                cfgs.extend(self._unfold_range_vm_section(cfg))
            return cfgs
        except RangeMappingError as e:
            e.log()
            raise SystemExit
        except UnknownKeyError as e:
            e.log()
            raise SystemExit
        except NonConfirmError:
            raise SystemExit
        except configparser.NoSectionError:
            # it's fine without _VMS_ section
            self.logger.info("No _VMS_ section defined")
            return []
        except ValueError:
            self.logger.info("Invalid value in section {0}".format(sec_def_key))
            raise SystemExit

    @staticmethod
    def _range_unfold_scatter(key, value):
        """scan scatter pattern and unfold range.


        Args:
            key (str)
            value (str)

        Returns:
            dict: for scatter mapping: {x:y}, if value defined in range,
                  return a dict with key: [value1, value2, ..] and values are
                  mapped in scatter way;
                  otherwise, return a dict with key: value
            int: mark (0 or 1) which records whether it has scatter range
            definition

        """

        scatter_re = r"[^\{]\{([\d]+:[\d]+)\}"
        scatter_range = re.findall(scatter_re, value)
        range_unfold = {}
        range_mark = 0
        if scatter_range:
            range_mark = 1
            range_unfold[key] = []
            start = int(scatter_range[0].split(":")[0])
            end = int(scatter_range[0].split(":")[1]) + 1
            range_value = "{" + scatter_range[0] + "}"
            for i in range(start, end):
                item = value.replace(range_value, str(i))
                range_unfold[key].append(item)
        else:
            range_unfold[key] = value
        return range_unfold, range_mark

    @staticmethod
    def _range_unfold_bunch(key, value):
        """scan bunch pattern and unfold range.

        Args:
            key (str)
            value (str)

        Returns:
            dict: for bunch mapping: {{x::y}}, if value defined in range,
            return a dict with key: [value1, value2, ..] and values are
            mapped in bunch way;
            otherwise, return a dict with key: value
            int: mark (0 or 1) which records whether it has bunch range
            definition

        """

        bunch_re = r"\{\{([\d]+:[\d]+)\}\}"
        bunch_range = re.findall(bunch_re, value)
        range_unfold = {}
        range_mark = 0
        if bunch_range:
            range_mark = 1
            range_unfold[key] = []
            start = int(bunch_range[0].split(":")[0])
            end = int(bunch_range[0].split(":")[1]) + 1
            range_value = "{{" + bunch_range[0] + "}}"
            for i in range(start, end):
                item = value.replace(range_value, str(i))
                range_unfold[key].append(item)
        else:
            range_unfold[key] = value
        return range_unfold, range_mark

    def _unfold_range_vm_section(self, cfg):
        """Pass the cfg dict and scan the range keys.
            If ranges are defined, unfold range.
            For VM section, other than VM name, several keys are supported for
            range definition. The return is different from _SVS_ or _DVS_
            sections. Here, when range is defined, it means multiple VMs.
            However, in _SVS_ or _DVS_, when range is defined, it means
            the switch consists of multiple hosts.

        Args:
            cfg (dict): the cfg dict return by initial reading

        Returns:
            list: a list of dicts, if value contains range, {key: value{1:10}}
                  will become [{key: value1}, {key, value2} .. {key: value10]
                  if no range, {key: value} will be [{key: value}]

        """

        # keys can be defined in a range
        range_keys = ["host", "datastore", "guest_hostname", "ip"]
        # use "vm" as pivot range key
        pivot = "vm"
        Check().check_kv(cfg, pivot, required=True)
        pivot_range_unfold, pivot_range_mark = self._range_unfold_scatter(
            pivot, cfg[pivot]
        )
        all_range = {}
        cfgs = []
        if not pivot_range_mark:
            cfgs.append(cfg)
            return cfgs
        range_unfold = {}
        for range_key in range_keys:
            if not Check().check_kv(cfg, range_key):
                continue
            # scatter range
            scatter_unfold, scatter_mark = self._range_unfold_scatter(
                range_key, cfg[range_key]
            )
            # bunch range
            bunch_unfold, bunch_mark = self._range_unfold_bunch(
                range_key, cfg[range_key]
            )
            # if it has scatter range, unfold it
            if scatter_mark:
                range_unfold[range_key] = self._scatter_mapping(
                    pivot_range_unfold[pivot],
                    scatter_unfold[range_key],
                )
            # if it has bunch range, unfold it
            if bunch_mark:
                range_unfold[range_key] = self._bunch_mapping(
                    pivot_range_unfold[pivot],
                    bunch_unfold[range_key],
                )
        # map the range key's range to pivot range ('vm')
        for idx, value in enumerate(pivot_range_unfold[pivot]):
            unfold_cfg = cfg
            unfold_cfg[pivot] = value
            for key in range_unfold.keys():
                unfold_cfg[key] = range_unfold[key][idx]
            cfgs.append(dict(unfold_cfg))
        all_range.update(pivot_range_unfold)
        all_range.update(range_unfold)
        self._plot_range(all_range)
        self._confirm_range()
        return cfgs

    @staticmethod
    def _plot_range(range_dicts):
        """plot range results"""

        table = Texttable()
        table_rows = []
        table_columns = []
        table_rows.append(range_dicts.keys())
        for key in range_dicts.keys():
            table_columns.append(range_dicts[key])
        for row in list(zip(*table_columns)):
            table_rows.append(row)
        table.add_rows(table_rows)
        table.set_deco(Texttable.VLINES | Texttable.HEADER)
        print(table.draw())
        print("\n")

    def _confirm_range(self):
        """Prompt user to confirm range definition"""

        confirm = input(
            "[ACTION] For the range definition, " "is this mapping what you expected? "
        )
        try:
            if strtobool(confirm) == 0:
                self.logger.info("Range not confirmed")
                raise NonConfirmError
            elif strtobool(confirm) == 1:
                self.logger.info("Range confirmed")
                return True
        except ValueError:
            self.logger.error("Not a valid answer for range confirmation")
            raise NonConfirmError

    @staticmethod
    def collect_scripts(vm_cfgs):
        """collect all scripts in vm_cfgs and return labeled and sorted
           scripts for further execution

        Args:
            vm_cfgs: a list of vm config dicts

        Returns:
            list: a nested list, each list contains a list of post config
                  tuple in sorted order

        """

        post_cfgs = []
        temp = []
        for vm_cfg in vm_cfgs:
            for key, value in vm_cfg.items():
                if key.startswith("script"):
                    Check().check_kv(vm_cfg, "guest_username", required=True)
                    Check().check_kv(vm_cfg, "guest_password", required=True)
                    temp.append(
                        (
                            vm_cfg["guest_username"],
                            vm_cfg["guest_password"],
                            vm_cfg["vm"],
                            value,
                            key,
                        )
                    )
        temp = sorted(temp, key=itemgetter(4))
        for _, g in itertools.groupby(temp, key=itemgetter(4)):
            post_cfgs.append(list(g))
        return post_cfgs

    def _add_item_svs_dvs(self, cfg, key, value):
        """_SVS_ or _DVS_ add key: value into cfg dict

        Args:
            cfg (dict): the existing cfg dict
            key (str)
            value (str)

        Returns:
            dict: the cfg with with added {key: value} where only certain keys
                   can be added.

        """

        str_keys = ["name", "port_group", "host", "datacenter"]
        int_keys = ["mtu"]
        list_keys = ["pnic"]
        try:
            if key in str_keys:
                cfg[key] = value
            elif key in list_keys:
                cfg[key] = self._find_list(value)
            elif key in int_keys:
                cfg[key] = int(value)
            else:
                raise UnknownKeyError(key)
        except UnknownKeyError as e:
            e.log()
            raise SystemExit

    @staticmethod
    def _find_list(s):
        """extract text between square brackets from a string
           and return a list. if no bracket, return original value.
           For example, '[a, b]' return [a,b], 'a' return 'a'

        Args:
            s (str)

        Returns:
            list or str

        """

        bracket_text = re.findall(r"\[(.*?)\]", s)
        if bracket_text:
            return eval(s)
        else:
            return s

    @staticmethod
    def _remove_space(s):
        """remove space before and after ":" or ","

        Args:
            s (str)

        Returns:
            str

        """

        s = re.sub(r"[\s]*:[\s]*", ":", s)
        s = re.sub(r"[\s]*,[\s]*", ",", s)
        return s

    def _add_item_vm(self, cfg, key, value):
        """_VM_ section add key: value into cfg dict

        Args:
            cfg (dict): the existing cfg dict
            key (str)
            value (str)

        Returns:
            dict: the cfg with with added {key: value} where only certain keys
                      can be added.

        """

        str_keys = [
            "template",
            "datacenter",
            "datastore",
            "cluster",
            "host",
            "vm_folder",
            "resource_pool",
            "latency",
            "guest_username",
            "guest_password",
            "port_group",
            "ip",
            "adapter_number",
            "netmask",
            "gateway",
            "domain",
            "guest_hostname",
            "vgpu",
            "pvrdma_port_group",
            "power",
            "dvs_name",
            "svs_name",
        ]
        float_keys = ["memory"]
        int_keys = [
            "cpu",
            "mmio_size",
            "cpu_shares",
            "memory_shares",
            "cores_per_socket",
        ]
        bool_keys = [
            "cpu_reservation",
            "memory_reservation",
            "is_dhcp",
            "linked",
            "instant",
            "secure_boot",
            "allow_guest_mtu_change",
        ]
        list_keys = ["device", "dns"]
        append_keys = ["script", "pf", "sriov_port_group", "sriov_dvs_name"]
        sequence_keys = ["sequence"]
        sequence_target = "script"
        if key in str_keys:
            cfg[key] = value
        elif key in list_keys:
            cfg[key] = self._find_list(value)
        elif key in append_keys:
            if not Check().check_kv(cfg, key):
                cfg[key] = []
            cfg[key].append(value)
        elif key in int_keys:
            cfg[key] = int(value)
        elif key in float_keys:
            cfg[key] = float(value)
        elif key in bool_keys:
            cfg[key] = strtobool(value)
        elif key in sequence_keys:
            labeled_sequence_target = sequence_target + str(value)
            cfg[labeled_sequence_target] = cfg[sequence_target]
            cfg[sequence_target] = []
        else:
            self.logger.error("Unknown key {0}".format(key))
            raise SystemExit
        return cfg


class Check(object):
    """
    a class for checking
    """

    def __init__(self):
        self.logger = log.my_logger(name=self.__class__.__name__)

    def check_kv(self, dict_to_check, key, none_check=True, required=False):
        """check key value existence"""
        if key in dict_to_check and dict_to_check[key]:
            return True
        if key in dict_to_check and not none_check:
            return True
        else:
            if required:
                self.logger.error("Please provide the value of {0}".format(key))
                raise SystemExit
            return False


class Error(Exception):
    pass


class UnknownKeyError(Error):
    def __init__(self, msg):
        self.msg = msg
        self.logger = log.my_logger(name=self.__class__.__name__)

    def log(self):
        self.logger.error("Unknown key {0}".format(self.msg))


class UnknownOpError(Error):
    def __init__(self, msg):
        self.msg = msg
        self.logger = log.my_logger(name=self.__class__.__name__)

    def log(self):
        self.logger.error("Unknown operation {0}".format(self.msg))


class NonConfirmError(Error):
    def __init__(self):
        self.logger = log.my_logger(name=self.__class__.__name__)

    def log(self):
        self.logger.error("Not confirmed")


class RangeMappingError(Error):
    def __init__(self):
        self.logger = log.my_logger(name=self.__class__.__name__)

    def log(self):
        self.logger.error(
            "Range definition is wrong. Couldn't do range " "mapping successfully."
        )

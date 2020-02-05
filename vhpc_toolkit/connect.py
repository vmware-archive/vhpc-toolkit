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
import atexit
import getpass
import os
import ssl
from distutils.util import strtobool

import yaml


try:
    from pyVim.connect import SmartConnect, Disconnect
except ModuleNotFoundError:
    from pyvim.connect import SmartConnect, Disconnect


def connect(host, username, password, port, keyfile=None, certfile=None):
    """ connect to vcenter and retrieve content

    Args:
        host (str):  name or IP of vCenter
        username (str): username of vCenter
        password (str): password of vCenter
        port (int): port number of vCenter
        keyfile (str): private vCenter keyfile
        certfile (str): certificate of vCenter

    Returns:
        ServiceContent: The properties of ServiceInstance,
                        which manages root object of vCenter inventory.

    """

    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    try:
        si = SmartConnect(
            host=host,
            user=username,
            pwd=password,
            port=port,
            sslContext=context,
            keyFile=keyfile,
            certFile=certfile,
        )
        content = si.content
    except Exception:
        print("[ERROR] Could not connect to vCenter")
        raise SystemExit
    atexit.register(Disconnect, si)
    return content


def get_global_config(kwargs):
    """

    Args:
        kwargs: namespace of config parameters

    Returns:
        dict: which contains global config properties,
    """

    global_config = {}
    for key, value in kwargs.items():
        if value is not None:
            global_config[key] = value
    return global_config


def get_vcenter_config():
    vcenter_config = {}
    vcenter_file = _find_vcenter_conf_file("vCenter.conf")
    try:
        f = open(vcenter_file, "r")
        loader = yaml.load(f, Loader=yaml.BaseLoader)
        vcenter_config.update(loader)
        f.close()
    except (OSError, TypeError):
        print("*** Not able to read vCenter server and username from config " "file.")
        raise SystemExit
    return check_vcenter_config(vcenter_config)


def check_vcenter_config(vcenter_config):
    """

    Args:
        vcenter_config: the vCenter config dictionary

    Returns:
        dict: vCenter_config dict after checking and completing with some
        defaults

    """

    from vhpc_toolkit.cluster import Check

    if not Check().check_kv(vcenter_config, "server"):
        print("*** Please provide vCenter server in config file.")
        raise SystemExit
    if not Check().check_kv(vcenter_config, "username"):
        print("*** Please provide vCenter username in config file")
        raise SystemExit
    if not Check().check_kv(vcenter_config, "port"):
        vcenter_config["port"] = 443  # vCenter default port
    if not Check().check_kv(vcenter_config, "password"):
        vcenter_config["password"] = getpass.getpass("vCenter password: ")
    if Check().check_kv(vcenter_config, "validate_certs"):
        vcenter_config["validate_certs"] = strtobool(vcenter_config["validate_certs"])
    else:
        vcenter_config["validate_certs"] = False
    if not Check().check_kv(vcenter_config, "certfile"):
        vcenter_config["certfile"] = None
    if not Check().check_kv(vcenter_config, "keyfile"):
        vcenter_config["keyfile"] = None
    return vcenter_config


def _find_vcenter_conf_file(file):
    """ locate the vcenter conf file

    Args:
        file (str): vcenter conf file

    Returns:
        Full path of the vcenter conf file if located (str)

    """

    from os.path import expanduser

    default_conf_dir = "../config"
    default_conf_dir = os.path.abspath(default_conf_dir)
    default_conf_file = "%s/%s" % (default_conf_dir, file)
    home_conf_dir = expanduser("~") + "/vhpc_toolkit"
    home_conf_dir = os.path.abspath(home_conf_dir)
    home_conf_file = "%s/%s" % (home_conf_dir, file)

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

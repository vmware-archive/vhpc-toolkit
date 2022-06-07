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
import os
import ssl

import hvac

from vhpc_toolkit import log

try:
    from pyVim.connect import SmartConnect, Disconnect
except ModuleNotFoundError:
    from pyvim.connect import SmartConnect, Disconnect


class Connect(object):
    """
    Connect to vCenter via credentials stored in Vault
    Alternative unsecured way is also provided.
    """

    def __init__(self):
        self.logger = log.my_logger(name=self.__class__.__name__)

    def connect_vcenter(
        self, server, username, password, port, is_vault, vault_secret_path
    ):
        """connect to vcenter and retrieve content

        Args:
            server (str):  name or IP of vCenter
            username (str): username of vCenter
            password (str): password of vCenter
            port (int): port number of vCenter
            is_vault (bool): whether the key has been encrypted by HashiCorp
                             Vault (https://www.vaultproject.io/)
            vault_secret_path(str): the secret path in vault, should be
                                    provided by user if they use Vault way to
                                    store their credentials

        Returns:
            ServiceContent: The properties of ServiceInstance,
                            which manages root object of vCenter inventory.

        """

        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        if is_vault:
            client = self.connect_vault()
            try:
                creds = client.secrets.kv.v2.read_secret_version(
                    path=vault_secret_path
                )["data"]["data"]
            except Exception as e:
                print("[ERROR] Error retrieving vault secrets: %s" % e)
                raise SystemExit
            server = creds[server]
            username = creds[username]
            password = creds[password]
        else:
            self.logger.warning(
                "Connecting to vCenter using unencrypted " "credentials"
            )
        try:
            si = SmartConnect(
                host=server,
                user=username,
                pwd=password,
                port=port,
                sslContext=context,
            )
            content = si.content
        except Exception as e:
            print("[ERROR] Error connecting to vCenter: %s" % e)
            raise SystemExit
        atexit.register(Disconnect, si)
        return content

    def connect_vault(self):
        """connect to VAULT using VAULT_ADDR and VAULT_TOKEN env variables

        Args: None
        Returns: VAULT client object

        """

        url = os.environ["VAULT_ADDR"]
        token = os.environ["VAULT_TOKEN"]
        if not url or not token:
            raise SystemExit(
                "Failed to connect to vault. "
                "Please set '`VAULT_ADDR` and `VAULT_TOKEN` in your "
                "environment.'"
            )
        try:
            client = hvac.Client(url=url, token=token)
        except Exception as e:
            self.logger.error("Error connecting to vault: %s" % e)
            raise SystemExit
        return client

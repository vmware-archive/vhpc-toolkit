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
import datetime
import logging


loggers = {}

LOG_FILE = "vhpc_toolkit"
FORMAT = "%(asctime)s %(name)s [%(levelname)s] %(message)s"


def my_logger(name=" ", log_level=logging.INFO, log_file=LOG_FILE):
    """get logger for logging

    Args:
        name (str): the name of this logger
        log_level (int): the effective level of this logger.
                         Typically logging.INFO or logging.DEBUG, which stores
                         as int
        log_file (str): the file for saving the logging info

    Returns:
        a logger object

    """

    global loggers
    if loggers.get(name):
        return loggers.get(name)
    else:
        logger = logging.getLogger(name)
        logging.basicConfig(level=log_level, format=FORMAT)
        logger.setLevel(log_level)
        now = datetime.datetime.now()
        handler = logging.FileHandler(log_file + now.strftime("-%Y-%m-%d") + ".log")
        handler.setLevel(log_level)
        formatter = logging.Formatter(FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        loggers.update({name: logger})
        return logger

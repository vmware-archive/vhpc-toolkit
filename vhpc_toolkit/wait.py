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
import time

from pyVmomi import vim

from vhpc_toolkit import log


class VMGetWait(object):
    """
    a class for waiting for VM related status
    """

    def __init__(self, vm_obj, timeout=300, sleep=5):
        """

        Args:
            vm_obj (vim.VirtualMachine)
            timeout (int): timeout for the waiting
            sleep (int): sleep seconds before rechecking

        """

        self.vm_obj = vm_obj
        self.timeout = timeout
        self.sleep = sleep
        self.logger = log.my_logger(name=self.__class__.__name__)

    def wait_for_ip(self):
        """

        Returns:
            str: the IP address of the VM if retrieved

        """

        waited = 0
        self.logger.info("Trying to get IP of VM {0}".format(self.vm_obj.name))
        while waited < self.timeout:
            ip_address = self.vm_obj.guest.ipAddress
            if ip_address is None:
                time.sleep(self.sleep)
                waited += self.sleep
            else:
                return ip_address
        self.logger.error("Couldn't get IP address for VM {0}".format(self.vm_obj.name))

    def wait_for_vmtools(self):
        """check vmtools status

        Returns:
            bool: if VM Tool is running, else raise exit.

        """

        waited = 0
        while waited < self.timeout:
            tools_status = self.vm_obj.guest.toolsRunningStatus
            if tools_status == "guestToolsRunning":
                return True
            elif tools_status == "toolsNotRunning" or "toolsNotInstalled":
                self.logger.info(
                    "Checking VMware Tools status "
                    "for VM {0}".format(self.vm_obj.name)
                )
                time.sleep(self.sleep)
                waited += self.sleep
            else:
                self.logger.info(
                    "VMware Tools status is unknown. "
                    "Waiting several seconds to check again"
                )
                time.sleep(self.sleep)
                waited += self.sleep
        self.logger.error(
            "VMware Tools status check time out. "
            "Post operation cannot be executed since VM {0} "
            "VMware Tools is not installed or "
            "running.".format(self.vm_obj.name)
        )
        raise SystemExit


class GetWait(object):
    """
    a class for waiting for vCenter tasks

    """

    def __init__(self, sleep=1):
        """

        Args:
            sleep (int): sleep seconds before rechecking

        """

        self.sleep = sleep
        self.logger = log.my_logger(name=self.__class__.__name__)

    def wait_for_tasks(self, tasks, task_name):
        """

        Args:
            tasks (Task): a list of Task objects to wait for. A Task object
                          is used to monitor and potentially cancel long
                          running operations.
            task_name: the task name of the list of tasks

        Returns:
            None

        """

        if not tasks:
            return
        for task in tasks:
            if task is None:
                continue
            task_done = False
            while not task_done:
                info = task.info
                if info.state == vim.TaskInfo.State.success:
                    task_done = True
                    self.logger.info(
                        "Task {0} (number {1}) is " "successful".format(task_name, task)
                    )
                elif info.state == vim.TaskInfo.State.queued:
                    self.logger.info(
                        "Task {0} (number {1}) is " "queued".format(task_name, task)
                    )
                    time.sleep(self.sleep)
                elif info.state == vim.TaskInfo.State.error:
                    task_done = True
                    self.logger.error(
                        "Task {0} (number {1}) has an error "
                        "- {2}".format(task_name, task, info.error.msg)
                    )
                else:
                    pass

    def wait_for_procs(self, proc_mng, procs, sleep=1):
        """wait a list of processes to finish in guest OS

        Args:
            proc_mng (guestOperationsManager.processManager)
            procs (a list of tuple): each tuple has process trace info,
                                    [(pid, auth, vm_obj)]
            sleep (int): sleep the number of seconds before re-checking

        Returns:
            None

        """

        for proc in procs:
            pid, auth, vm_obj = proc
            proc_info = proc_mng.ListProcessesInGuest(vm_obj, auth, [pid])
            while not proc_info[0].endTime:
                time.sleep(sleep)
                proc_info = proc_mng.ListProcessesInGuest(vm_obj, auth, [pid])
            exit_code = proc_info[0].exitCode
            if exit_code == 0:
                self.logger.info("Process {0} completed successfully".format(pid))
            elif exit_code != 0:
                self.logger.error("Process {0} is finished with an error".format(pid))
                raise SystemExit

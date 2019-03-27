#!/usr/bin/env python

# Copyright (C) 2018  Jan Kotanski, S2Innovation
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in  version 3
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.
#

import time
import tango
import socket
import sys
import whichcraft
import subprocess
import os
from multiprocessing import Process


#: python3 running
PY3 = (sys.version_info > (3,))


class Starter(Process):
    """ device starter
    """

    def __init__(self, devices, stqueue):
        """ constructor"""
        Process.__init__(self)
        self.__stqueue = stqueue
        self.__devices = devices

        self.__launched = []
        self.__registered_servers = []
        self.__registered_devices = []

    def run(self):
        """ worker thread
        """
        if hasattr(tango.ApiUtil, 'cleanup'):
            tango.ApiUtil.cleanup()
        self.__db = tango.Database()
        starters = self.__db.get_device_exported_for_class(
            "Starter").value_string
        try:
            self.__starter = tango.DeviceProxy(starters[0])
        except Exception:
            self.__starter = None

        for device in self.__devices:
            self.register(**device)
            self.launch(**device)
        self.__stqueue.put(
            (tuple(self.__registered_servers),
             tuple(self.__registered_devices),
             tuple(self.__launched)))

    def register(self, device_class=None, server_instance=None,
                 target_device=None, host=None, stop=True):
        """create device

        :param device_class: device class
        :type device_class: :obj:`str`
        :param server_instance: server instance
        :type server_instance: :obj:`str`
        :param target_device: target device
        :type target_device: :obj:`str`
        :param host: host name
        :type host: :obj:`str`
        :param stop: mark server to be stopped
        :type stop: :obj:`bool`
        """

        servers = self.__db.get_server_list(server_instance).value_string
        devices = self.__db.get_device_exported_for_class(
            device_class).value_string
        new_device = tango.DbDevInfo()
        new_device._class = device_class
        new_device.server = server_instance
        new_device.name = target_device
        if not servers:
            if target_device in devices:
                raise Exception(
                    "Device %s exists in different server" % device_class)
            self.__db.add_device(new_device)
            self.__db.add_server(new_device.server, new_device)
            if stop:
                self.__registered_servers.append(new_device.server)
                self.__registered_devices.append(target_device)
        else:
            if target_device not in devices:
                self.__db.add_device(new_device)
                if stop:
                    self.__registered_devices.append(target_device)
            else:
                pass

    def launch(self, device_class=None, server_instance=None,
               target_device=None, host=None, stop=True, verbose=False):
        """launch device

        :param device_class: device class
        :type device_class: :obj:`str`
        :param server_instance: server instance
        :type server_instance: :obj:`str`
        :param target_device: target device
        :type target_device: :obj:`str`
        :param host: host name
        :type host: :obj:`str`
        :param stop: mark server to be stopped
        :type stop: :obj:`bool`
        :param verbose: verbose mode
        :type verbose: :obj:`bool`
        """
        startcmd = None
        running = []
        server = self.__db.get_server_class_list(server_instance)
        if len(server) == 0:
            raise Exception('Server ' + server_instance.split('/')[0]
                            + ' not defined in database\n')

        sinfo = self.__db.get_server_info(server_instance)
        sinfo.name = server_instance
        sinfo.host = host or socket.gethostname()
        sinfo.mode = 1
        sinfo.level = 1
        self.__db.put_server_info(sinfo)

        # if self.__starter:
        #     self.__starter.UpdateServersInfo()
        #     running = self.__starter.DevGetRunningServers(True)
        found = False
        found = self.checkDevice(target_device, 1)

        if not found and server_instance not in running:
            try:
                self.__starter.DevStart(server_instance)
                if not self.checkDevice(target_device):
                    raise Exception(
                        "Server %s start failed" % server_instance)
            except Exception:
                startcmd = ""
                sev_ins = server_instance.split("/")
                if whichcraft.which(sev_ins[0]) is not None:
                    startcmd = "%s %s &" % (sev_ins[0], sev_ins[1])
                elif server_instance.startswith("PyBenchmarkTarget/"):
                    if PY3:
                        if os.path.isdir(
                                "../ds/PyBenchmarkTarget/PyBenchmarkTarget"):
                            startcmd = \
                                "cd ../ds/PyBenchmarkTarget/; " \
                                "python3 ./PyBenchmarkTarget %s &" % \
                                sev_ins[1]
                    else:
                        if os.path.isdir(
                                "../ds/PyBenchmarkTarget/PyBenchmarkTarget"):
                            startcmd = \
                                "cd ../ds/PyBenchmarkTarget/; " \
                                "python2 ./PyBenchmarkTarget %s &" % \
                                sev_ins[1]

                elif server_instance.startswith("JavaBenchmarkTarget/"):
                    if os.path.isfile(
                            "../ds/JavaBenchmarkTarget/target/"
                            "JavaBenchmarkTarget-1.0.jar"
                    ):

                        startcmd = \
                            "cd ../ds/JavaBenchmarkTarget; " \
                            "CLASSPATH=/usr/share/java/JTango.jar:" \
                            "./target/" \
                            "JavaBenchmarkTarget-1.0.jar:$CLASSPATH;" \
                            "export CLASSPATH; . /etc/tangorc; " \
                            "export TANGO_HOST; " \
                            "java  org.tango.javabenchmarktarget." \
                            "JavaBenchmarkTarget %s &" % \
                            (sev_ins[1])
                        pass
                elif server_instance.startswith("CppBenchmarkTarget/"):
                    home = os.path.expanduser("~")
                    if os.path.isfile(
                            "%s/DeviceServers/CppBenchmarkTarget" % home):
                        serverfile = "%s/DeviceServers/CppBenchmarkTarget" % \
                                     home
                        startcmd = "%s %s &" % (serverfile, sev_ins[1])
                else:
                    pass
                if startcmd:
                    # os.system(startcmd)
                    self._psub = subprocess.call(
                        startcmd, stdout=None, stderr=None, shell=True)
                else:
                    raise Exception(
                        "Server %s cannot be found " % server_instance)
                pass
        if verbose:
            sys.stdout.write("waiting for server")
        if not self.checkDevice(target_device):
            raise Exception("Server %s start failed" % server_instance)
        if not found:
            if stop:
                self.__launched.append(server_instance)

    def checkDevice(self, dvname, maxtime=10, verbose=False):
        """ waits for tango device

        :param dvname: tango device name
        :type dvname: :obj:`str`
        :param maxtime: maximal time in sec
        :type maxtime: :obj:`float`
        :param verbose: verbose mode
        :type verbose: :obj:`bool`
        :returns: if tango device ready
        :rtype: :obj:`bool`
        """
        maxcnt = int(maxtime * 100)
        found = False
        cnt = 0
        while not found and cnt < maxcnt:
            try:
                if verbose:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                if hasattr(self, '__Starter_db') and self.__db is not None:
                    exl = self.__db.get_device_exported(dvname)
                    if dvname not in exl.value_string:
                        time.sleep(0.01)
                        cnt += 1
                        continue
                device = tango.DeviceProxy(dvname)
                time.sleep(0.01)
                device.ping()
                device.state()
                found = True
                if verbose:
                    print("%s: %s is working" % (cnt, device))
            except Exception as e:
                if verbose:
                    print(str(e))
                found = False
            cnt += 1
        return found


class Stoper(Process):
    """ device stoper
    """

    def __init__(self, servers, devices, launched):
        """ constructor"""

        Process.__init__(self)
        self.__launched = list(launched)
        self.__registered_servers = list(servers)
        self.__registered_devices = list(devices)

    def run(self):
        """ worker thread
        """
        if hasattr(tango.ApiUtil, 'cleanup'):
            tango.ApiUtil.cleanup()
        self.__db = tango.Database()
        starters = self.__db.get_device_exported_for_class(
            "Starter").value_string
        try:
            self.__starter = tango.DeviceProxy(starters[0])
        except Exception:
            self.__starter = None
        self.stopServers()
        self.unregisterServers()

    def stopServers(self):
        """ stop launched devices
        """
        for server_instance in self.__launched:
            try:
                self.__starter.DevStop(server_instance)
                # self.__starter.HardKillServer(server_instance)
            except Exception:
                server, instance = server_instance.split("/")
                grepserver = \
                    "ps -ef | grep '%s %s' | grep -v grep" % \
                    (server, instance)
                if PY3:
                    with subprocess.Popen(grepserver,
                                          stdout=subprocess.PIPE,
                                          shell=True) as proc:
                        try:
                            outs, errs = proc.communicate(timeout=15)
                        except subprocess.TimeoutExpired:
                            proc.kill()
                            outs, errs = proc.communicate()
                        res = str(outs, "utf8").split("\n")
                        for r in res:
                            sr = r.split()
                            if len(sr) > 2:
                                subprocess.call(
                                    "kill -9 %s" % sr[1],
                                    stderr=None,
                                    shell=True)
                else:
                    pipe = subprocess.Popen(
                        grepserver,
                        stdout=subprocess.PIPE,
                        shell=True).stdout

                    res = str(pipe.read()).split("\n")
                    for r in res:
                        sr = r.split()
                        if len(sr) > 2:
                            subprocess.call(
                                "kill -9 %s" % sr[1],
                                stderr=None,
                                shell=True)
                    pipe.close()
        self.__launched = []

    def unregisterServers(self):
        """ unregister registered devices
        """
        for dv in self.__registered_devices:
            self.__db.delete_device(dv)
        for server in self.__registered_servers:
            self.__db.delete_server(server)
        self.__registered_servers = []

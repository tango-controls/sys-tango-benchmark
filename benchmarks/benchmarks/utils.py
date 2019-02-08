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

import numpy as np
import time
import pytz
import datetime
import csv
import PyTango
import socket
import sys
import whichcraft
import subprocess
import os


TIMEOUTS = True


#: python3 running
PY3 = (sys.version_info > (3,))


class CSVOutput(object):
    """ creates CSV output
    """

    def __init__(self, filename, options):
        """ constructor

        :param filename: file name
        :type filename: :obj:`str`
        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """
        #: (:obj:`str`) filename
        self._filename = filename
        #: (:obj:`list` <:obj:`str`> ) hidden options
        self.__hidden = ["title", "description",
                         "verbose", "version"]

        #: (:obj:`str`) title
        self._title = options.title
        #: (:obj:`str`) description
        self._description = options.description
        #: (:obj:`str`) date and time
        self._date = self.__currenttime()

        #: (:obj:`dict` <:obj:`str`, `any` >)
        #  dictionary with options
        self._dictoptions = dict(options.__dict__)
        for key in list(self._dictoptions.keys()):
            if key in self.__hidden:
                self._dictoptions.pop(key)
        #: (:class:`File`) output file
        self._csvfile = None
        #: (:class:`csv.Writer`) CSV writer
        self._writer = None

    def __currenttime(self, witht=False):
        """ returns current time string

        :returns: current time
        :rtype: :obj:`str`
        """
        tzone = time.tzname[0]
        tz = pytz.timezone(tzone)
        if witht:
            fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
        else:
            fmt = '%Y-%m-%d %H:%M:%S.%f%z'
        starttime = tz.localize(datetime.datetime.now())
        return str(starttime.strftime(fmt))

    def printInfo(self):
        """ shows general info
        """
        self._csvfile = open(self._filename, 'w')
        self._writer = csv.writer(self._csvfile)
        self._writer.writerow([self._title])
        self._writer.writerow([self._date])
        self._writer.writerow(
            [
                ("%s=%s" % (key, self._dictoptions[key] or ""))
                for key in sorted(self._dictoptions.keys())])

    def printHeader(self, labels):
        """ shows header

        :param labels: labels list
        :type labels: :obj:`list` <:obj:`str`>
        """
        self._writer.writerow([lb.strip() for lb in labels])

    def printLine(self, records):
        """ shows header

        :param record: record list
        :type record: :obj:`list` <:obj:`str`>
        """
        self._writer.writerow(records)

    def printEnd(self):
        """ shows header
        """
        self._csvfile.close()


class RSTOutput(object):
    """ creates RST output
    """

    def __init__(self, options):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """
        #: (:obj:`list` <:obj:`str`> ) hidden options
        self.__hidden = ["title", "description",
                         "verbose", "version"]

        #: (:obj:`str`) title
        self._title = options.title
        #: (:obj:`str`) description
        self._description = options.description
        #: (:obj:`str`) date and time
        self._date = self.__currenttime()
        #: (:obj:`list` <:obj:`int`> ) headers sizes
        self._hsizes = []

        #: (:obj:`dict` <:obj:`str`, `any` >)
        #  dictionary with options
        self._dictoptions = dict(options.__dict__)
        for key in list(self._dictoptions.keys()):
            if key in self.__hidden:
                self._dictoptions.pop(key)

    def __currenttime(self):
        """ returns current time string

        :returns: current time
        :rtype: :obj:`str`
        """
        tzone = time.tzname[0]
        tz = pytz.timezone(tzone)
        # fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
        fmt = '%Y-%m-%d %H:%M:%S.%f%z'
        starttime = tz.localize(datetime.datetime.now())
        return str(starttime.strftime(fmt))

    def printInfo(self):
        """ shows general info
        """
        print("")
        print(self._title)
        print("=" * len(self._title))
        print("")
        print(self._description)
        print("")
        print("**Date:** %s" % self._date)
        print("")
        print("Benchmark setup")
        print("---------------")
        print("")
        for key in sorted(self._dictoptions.keys()):
            print("%s=%s" % (key, self._dictoptions[key] or ""))
        print("")
        print("Results")
        print("-------")
        print("")

    def printHeader(self, labels):
        """ shows header

        :param labels: labels list
        :type labels: :obj:`list` <:obj:`str`>
        """
        self._hsizes = [len(lb) for lb in labels]

        print((" ").join(["=" * (2 + sz) for sz in self._hsizes]))
        print(" " + ("   ").join(labels))
        print((" ").join(["=" * (2 + sz) for sz in self._hsizes]))

    def printLine(self, records):
        """ shows header

        :param record: record list
        :type record: :obj:`list` <:obj:`str`>
        """
        lrecords = [str(rc) + " " * (self._hsizes[i] - len(str(rc)))
                    for i, rc in enumerate(records)]
        print(" " + ("   ").join(lrecords))

    def printEnd(self):
        """ shows header
        """
        print((" ").join(["=" * (2 + sz) for sz in self._hsizes]))
        print("")


class Benchmark(object):
    """  master class for read benchmark
    """

    def __init__(self):
        """ constructor

        """

        #: (:obj:`list` < :class:`multiprocessing.Queue` >) result queues
        self._qresults = []
        #: (:obj:`list` < :class:`Result` >) result list
        self._results = []
        #: (:obj:`list` < :class:`Worker` >) process worker
        self._workers = []

    def start(self):
        """ start benchmark
        """
        for wk in self._workers:
            wk.start()
        for wk in self._workers:
            wk.join()

    def fetchResults(self, verbose):
        """ fetches the results from queue

        :param verbose: verbose mode
        :type verbose: :obj:`bool`
        """
        self._results = []
        for qres in self._qresults:
            try:
                res = qres.get(block=False)
                self._results.append(res)
                if verbose:
                    print("VERBOSE: id: %s,  counts: %s,  "
                          "speed: %s counts/s,  time: %s s" %
                          (res.wid, res.counts,
                           res.speed(), res.ctime))
            except Exception:
                pass

    def output(self, show=False):
        """ shows a simple output

        :param show: show output flag
        :type show: :obj:`type`
        :rtype: :obj:`dict` <:obj:`str`, :obj:`str`>
        :returns: output dictionary
        """

        avg = Average(self._results)
        nn = avg.size()
        mcnts = avg.counts()
        mtm = avg.ctime()
        mspd = avg.speed()
        # mspd = avg.simplespeed()
        scnts = [nn * vl for vl in mcnts]
        sspd = [nn * vl for vl in mspd]
        prc = "%s"
        prs = "%s"
        prsc = "%s"
        prss = "%s"
        prt = "%s"
        if mcnts[1]:
            prc = "%." + str(
                max(0, int(2 - np.log10(
                    mcnts[1] if mcnts[1] > 10e-16 else 10e-16
                )))
            ) + "f"
        if mspd[1]:
            prs = "%." + str(
                max(0, int(2 - np.log10(
                    mspd[1] if mspd[1] > 10e-16 else 10e-16
                )))
            ) + "f"
        if scnts[1]:
            prsc = "%." + str(
                max(0, int(2 - np.log10(
                    scnts[1] if mcnts[1] > 10e-16 else 10e-16
                )))
            ) + "f"
        if sspd[1]:
            prss = "%." + str(
                max(0, int(2 - np.log10(
                    sspd[1] if sspd[1] > 10e-16 else 10e-16
                )))
            ) + "f"
        if mtm[1]:
            prt = "%." + str(
                max(0, int(2 - np.log10(
                    mtm[1] if mtm[1] > 10e-16 else 10e-16
                )))
            ) + "f"

        if show:
            fmt = "no_clients: %i,  counts: " + prc + " +/- " + prc + \
                  ",  speed: (" + prs + " +/- " + prs + ") counts/s" \
                  ",  time: (" + prt + " +/- " + prt + ") s "
            print(fmt % (nn,
                         float(mcnts[0]), float(mcnts[1]),
                         float(mspd[0]), float(mspd[1]),
                         float(mtm[0]), float(mtm[1])))
        res = {}
        res["no_clients"] = str(nn)
        res["counts"] = prc % float(mcnts[0])
        res["err_counts"] = prc % float(mcnts[1])
        res["speed"] = prs % float(mspd[0])
        res["err_speed"] = prs % float(mspd[1])
        res["sumcounts"] = prsc % float(scnts[0])
        res["err_sumcounts"] = prsc % float(scnts[1])
        res["sumspeed"] = prss % float(sspd[0])
        res["err_sumspeed"] = prss % float(sspd[1])
        res["time"] = prt % float(mtm[0])
        res["err_time"] = prt % float(mtm[1])
        return res


class Result(object):
    """ benchmark result
    """

    def __init__(self, wid, counts, ctime):
        """ constructor

        :param wid: worker id
        :type wid: :obj:`int`
        :param counts: benchmark counts
        :type counts: :obj:`int`
        :param ctime: counting time in s
        :type ctime: :obj:`float`
        """
        #: (:obj:`int`) worker id
        self.wid = wid
        #: (:obj:`int`) benchmark counts
        self.counts = counts
        #: (:obj:`float`) counting time in s
        self.ctime = ctime

    def speed(self):
        """ provides counting speed

        :rtype: :obj:`float`
        :returns: counting speed
        """
        return self.counts / self.ctime


class Average(object):
    """ benchmark result
    """

    def __init__(self, results):
        """ constructor

        :param results: a list of results
        :type results: :obj:`list` <:class:`Result`>
        """
        self.__results = results

    def counts(self):
        """ provides mean counts and its standard deviation
        std = sqrt(mean(abs(x - x.mean())**2))

        :rtype: (:class:`numpy.float`, :class:`numpy.float`)
        :returns: mean counts, std
        """
        cnts = [res.counts for res in self.__results]
        return np.mean(cnts), np.std(cnts)

    def ctime(self):
        """ provides mean time and its standard deviation
        std = sqrt(mean(abs(x - x.mean())**2))

        :rtype: (:class:`numpy.float`, :class:`numpy.float`)
        :returns: mean time, std
        """
        ctms = [res.ctime for res in self.__results]
        return np.mean(ctms), np.std(ctms)

    def speed(self):
        """ provides mean time and its standard deviation
        std_f ** 2 = (d_t f) ** 2 * std_t ** 2 + (d_c f) ** 2 *  std_c ** 2

        :rtype: (:class:`numpy.float`, :class:`numpy.float`)
        :returns: mean time, std
        """
        # ctms = [res.speed() for res in self.__results]
        # return np.mean(ctms), np.std(ctms)

        mtm = self.ctime()
        mcnts = self.counts()
        mean = mcnts[0]/mtm[0]
        std = np.sqrt(
            mcnts[1] ** 2 / mtm[0] ** 2 +
            mtm[1] ** 2 * mcnts[0] ** 2 / (mtm[0] ** 4))
        return mean, std

    def simplespeed(self):
        """ provides mean time and its standard deviation
        std = sqrt(mean(abs(x - x.mean())**2))
        from aproximated formula
        (anyhow we dont know distribution of counts and time)

        :rtype: (:class:`numpy.float`, :class:`numpy.float`)
        :returns: mean time, std
        """
        ctms = [res.speed() for res in self.__results]
        return np.mean(ctms), np.std(ctms)

    def size(self):
        """ provides number of results

        :rtype: int
        :returns: number of results
        """
        return len(self.__results)


class Starter(object):
    """ device starter
    """

    def __init__(self):
        """ constructor"""

        self.__db = PyTango.Database()
        starters = self.__db.get_device_exported_for_class(
            "Starter").value_string
        try:
            self.__starter = PyTango.DeviceProxy(starters[0])
        except Exception:
            self.__starter = None

        self.__launched = []
        self.__registered_servers = []
        self.__registered_devices = []

    def register(self, device_class=None, server_instance=None,
                 target_device=None, host=None):
        """create device

        :param device_class: device class
        :type device_class: :obj:`str`
        :param server_instance: server instance
        :type server_instance: :obj:`str`
        :param target_device: target device
        :type target_device: :obj:`str`
        :param host: host name
        :type host: :obj:`str`
        """

        servers = self.__db.get_server_list(server_instance).value_string
        devices = self.__db.get_device_exported_for_class(
            device_class).value_string
        new_device = PyTango.DbDevInfo()
        new_device._class = device_class
        new_device.server = server_instance
        new_device.name = target_device
        if not servers:
            if target_device in devices:
                raise Exception(
                    "Device %s exists in different server" % device_class)
            self.__db.add_device(new_device)
            self.__db.add_server(new_device.server, new_device)
            self.__registered_servers.append(new_device.server)
            self.__registered_devices.append(target_device)
        else:
            if target_device not in devices:
                self.__db.add_device(new_device)
                self.__registered_devices.append(target_device)
            else:
                pass

    def launch(self, device_class=None, server_instance=None,
               target_device=None, host=None, verbose=False):
        """launch device

        :param device_class: device class
        :type device_class: :obj:`str`
        :param server_instance: server instance
        :type server_instance: :obj:`str`
        :param target_device: target device
        :type target_device: :obj:`str`
        :param host: host name
        :type host: :obj:`str`
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
        if TIMEOUTS:
            found = self.checkDevice(
                PyTango.DeviceProxy(target_device), 1)

        if not found and server_instance not in running:
            try:
                self.__starter.DevStart(server_instance)
                if TIMEOUTS:
                    if not self.checkDevice(PyTango.DeviceProxy(
                            target_device)):
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
        if TIMEOUTS:
            if not self.checkDevice(PyTango.DeviceProxy(
                    target_device)):
                raise Exception("Server %s start failed" % server_instance)
        if TIMEOUTS and not found:
            self.__launched.append(server_instance)

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

    @classmethod
    def checkDevice(cls, device, maxtime=10, verbose=False):
        """ waits for tango device

        :param device: tango device name
        :type device: :class:`PyTango.DeviceProxy`
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

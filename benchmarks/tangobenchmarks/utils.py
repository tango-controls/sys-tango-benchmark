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
import sys

from multiprocessing import Queue


#: python3 running
PY3 = (sys.version_info > (3,))


class Benchmark(object):
    """  master class for read benchmark
    """

    def __init__(self, worker_class, options, extra_options):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """

        #: (:obj:`list` < :class:`Result` >) result list
        self._results = []
        #: (:obj:`list` < :class:`multiprocessing.Queue` >) result queues
        self._qresults = [Queue() for i in range(options.clients)]
        #: (:obj:`list` < :class:`Worker` >) process worker
        self._workers = [
            worker_class(i, q, options, **extra_options)
            for i, q in enumerate(self._qresults)
        ]

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
        errs = avg.errorsum()
        print(errs)
        # mspd = avg.simplespeed()
        scnts = [nn * vl for vl in mcnts]
        sspd = [nn * vl for vl in mspd]
        prc = "%s"
        prs = "%s"
        prsc = "%s"
        prss = "%s"
        prt = "%s"
        perrs = "%s"
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
        res["sd_counts"] = prc % float(mcnts[1])
        res["speed"] = prs % float(mspd[0])
        res["sd_speed"] = prs % float(mspd[1])
        res["sumcounts"] = prsc % float(scnts[0])
        res["sd_sumcounts"] = prsc % float(scnts[1])
        res["sumspeed"] = prss % float(sspd[0])
        res["sd_sumspeed"] = prss % float(sspd[1])
        res["time"] = prt % float(mtm[0])
        res["sd_time"] = prt % float(mtm[1])
        res["error_sum"] = perrs % int(errs)
        return res


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
                         "verbose", "version", "worker", "worker_program"]

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


class Result(object):
    """ benchmark result
    """

    def __init__(self, wid, counts, ctime, errors=None):
        """ constructor

        :param wid: worker id
        :type wid: :obj:`int`
        :param counts: benchmark counts
        :type counts: :obj:`int`
        :param ctime: counting time in s
        :type ctime: :obj:`float`
        :param counts: error counts
        :type counts: :obj:`int`
        """
        #: (:obj:`int`) worker id
        self.wid = wid
        #: (:obj:`int`) benchmark counts
        self.counts = counts
        #: (:obj:`float`) counting time in s
        self.ctime = ctime
        #: (:obj:`int`) benchmark error counts
        self.errors = errors

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

    def errorsum(self):
        """ provides sum of errors

        :rtype: int
        :returns: error sum
        """
        errs = [res.errors for res in self.__results]
        return np.sum(errs)

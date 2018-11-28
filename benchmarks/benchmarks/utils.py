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


class Benchmark(object):
    """  master class for read benchmark
    """

    def __init__(self):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
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

    def fetchresults(self, verbose):
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

    def output(self):
        """ shows a simple output
        """

        avg = Average(self._results)
        mcnts = avg.counts()
        mtm = avg.ctime()
        mspd = avg.speed()
        mspd = avg.speed()
        # mspd = avg.simplespeed()
        prc = "%s"
        prt = "%s"
        prs = "%s"
        if mcnts[1]:
            prc = "%." + str(max(0, int(2 - np.log10(mcnts[1])))) + "f"
        if mtm[1]:
            prt = "%." + str(max(0, int(2 - np.log10(mtm[1])))) + "f"
        if mspd[1]:
            prs = "%." + str(max(0, int(2 - np.log10(mspd[1])))) + "f"

        fmt = "nr_clients: %i,  counts: " + prc + " +/- " + prc + \
              ",  speed: (" + prs + " +/- " + prs + ") counts/s" \
              ",  time: (" + prt + " +/- " + prt + ") s "
        print(fmt % (avg.size(),
                     float(mcnts[0]), float(mcnts[1]),
                     float(mspd[0]), float(mspd[1]),
                     float(mtm[0]), float(mtm[1])))

        # print("nr: %i, counts: %f +/- %f, time: (%f +/- %f) s, "
        #       "speed: (%f +/- %f) counts/s" % (
        #               avg.size(),
        #               mcnts[0], mcnts[1],
        #               mtm[0], mtm[1],
        #               mspd[0], mspd[1]))


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

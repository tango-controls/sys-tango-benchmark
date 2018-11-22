#!/usr/bin/env python

# Copyright (C) 2018  Jan Kotanski, S2Innovation
#
# lavue is an image viewing program for photon science imaging detectors.
# Its usual application is as a live viewer using hidra as data source.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in  version 2
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

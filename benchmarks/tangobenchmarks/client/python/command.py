import tango
import time
import multiprocessing

import tangobenchmarks.utils as utils


class Worker(multiprocessing.Process):
    """ worker instance
    """

    def __init__(self, wid, qresult, options):
        """ constructor

        :param wid: worker id
        :type wid: :obj:`int`
        :param qresult: queue with result
        :type qresult: :class:`Queue.Queue` or `queue.queue`

        """
        multiprocessing.Process.__init__(self)

        # : (:obj:`int`) worker id
        self.__wid = wid
        # : (:obj:`float`) time period in seconds
        self.__period = float(options.period)
        #: (:obj:`str`) device proxy
        self.__device = options.device
        #: (:obj:`str`) device command name
        self.__command = options.command
        # : (:class:`tango.DeviceProxy`) device proxy
        self.__proxy = None
        # : (:class:`Queue.Queue`) result queue
        self.__qresult = qresult
        # : (:obj:`int`) counter
        self.__counter = 0

    def run(self):
        """ worker thread
        """
        if hasattr(tango.ApiUtil, 'cleanup'):
            tango.ApiUtil.cleanup()
        self.__proxy = tango.DeviceProxy(self.__device)
        stime = time.time()
        etime = stime
        while etime - stime < self.__period:
            self.__proxy.command_inout(self.__command)
            etime = time.time()
            self.__counter += 1
        self.__qresult.put(
            utils.Result(self.__wid, self.__counter, etime - stime))

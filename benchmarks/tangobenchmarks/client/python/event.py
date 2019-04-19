import tango
import time
from multiprocessing import Process, Queue

import tangobenchmarks.utils as utils


def cb_tango(*args):
    """ tango callback
    """
    event_data = args[0]
    if event_data.err:
        print(event_data.errors)


class Worker(Process):
    """ worker instance
    """

    def __init__(self, wid, device, attribute, period, qresult):
        """ constructor

        :param wid: worker id
        :type wid: :obj:`int`
        :param device: device name
        :type device: :obj:`str`
        :param attribute: attribute name
        :type attribute: :obj:`str`
        :param period: time period
        :type period: :obj:`float`
        :param qresult: queue with result
        :type qresult: :class:`Queue.Queue` or `queue.queue`

        """
        Process.__init__(self)

        # : (:obj:`int`) worker id
        self.__wid = wid
        # : (:obj:`float`) time period in seconds
        self.__period = float(period)
        #: (:obj:`str`) device proxy
        self.__device = device
        #: (:obj:`str`) device attribute name
        self.__attribute = attribute
        # : (:class:`tango.AttributeProxy`) attribute proxy
        self.__proxy = None
        # : (:class:`Queue.Queue`) result queue
        self.__qresult = qresult
        # : (:obj:`int`) counter
        self.__counter = 0
        # : (:obj:`int`) error counter
        self.__errors = 0

    def run(self):
        """ worker thread
        """
        if hasattr(tango.ApiUtil, 'cleanup'):
            tango.ApiUtil.cleanup()
        self.__proxy = tango.DeviceProxy(self.__device)

        stime = time.time()
        etime = stime
        ids = []
        while etime - stime < self.__period:
            try:
                id_ = self.__proxy.subscribe_event(
                    self.__attribute,
                    tango.EventType.CHANGE_EVENT,
                    cb_tango)
                ids.append(id_)
            except Exception:
                self.__errors += 1
            else:
                self.__counter += 1
            etime = time.time()
        for id_ in ids:
            self.__proxy.unsubscribe_event(id_)
        self.__qresult.put(
            utils.Result(self.__wid, self.__counter, etime - stime,
                         self.__errors))

import tango
import time
import multiprocessing
# import threading

import tangobenchmarks.utils as utils


class TangoCounterCb(object):
    """callback class which counts events
    """

    def __init__(self):
        self.counter = 0
        self.errors = 0
        # self.lock = threading.Lock()

    def push_event(self, *args, **kwargs):
        """callback method receiving the event
        """
        # with self.lock:
        event_data = args[0]
        if event_data.err:
            self.errors += 1
            # print(event_data.err)
        else:
            self.counter += 1


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
        # : (:obj:`float`) event period in milliseconds
        self.__speriod = float(options.speriod)
        #: (:obj:`str`) device proxy
        self.__device = options.device
        #: (:obj:`str`) device attribute name
        self.__attribute = options.attribute
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
        self.__proxy.set_timeout_millis(10000)

        counter_cb = TangoCounterCb()

        id_ = self.__proxy.subscribe_event(
            self.__attribute,
            tango.EventType.CHANGE_EVENT,
            counter_cb)
        self.__proxy.EventAttribute = self.__attribute
        self.__proxy.EventSleepPeriod = self.__speriod
        time.sleep(1)
        stime = time.time()
        etime = stime
        self.__proxy.StartEvents()
        time.sleep(self.__period)
        finished = False
        while finished:
            try:
                self.__proxy.StopEvents()
                finished = True
            except tango.DevFailed:
                # print(str(e))
                self.__errors += 1
        etime = time.time()
        time.sleep(1)
        self.__proxy.unsubscribe_event(id_)
        self.__counter = counter_cb.counter
        self.__errors += counter_cb.errors
        self.__qresult.put(
            utils.Result(self.__wid, self.__counter, etime - stime,
                         self.__errors))

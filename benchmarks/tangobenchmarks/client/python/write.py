import tango
import time
import multiprocessing

import tangobenchmarks.utils as utils


class Worker(multiprocessing.Process):
    """ worker instance
    """

    def __init__(self, wid, qresult, options, value):
        """ constructor

        :param wid: worker id
        :type wid: :obj:`int`
        :param value:  attribute value
        :type value: :class:`numpy.ndarray`
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
        #: (:obj:`str`) device attribute name
        self.__attribute = options.attribute
        #: (:obj:`float` or :class:`np.array`) device attribute value
        self.__value = value
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
        while etime - stime < self.__period:
            try:
                self.__proxy.write_attribute(
                    self.__attribute, self.__value)
            except Exception:
                self.__errors += 1
            else:
                self.__counter += 1
            etime = time.time()
        self.__qresult.put(
            utils.Result(self.__wid, self.__counter, etime - stime,
                         self.__errors))

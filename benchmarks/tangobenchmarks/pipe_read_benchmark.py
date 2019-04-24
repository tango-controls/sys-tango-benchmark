import argparse
import sys

from argparse import RawTextHelpFormatter
from multiprocessing import Queue

from . import release
from . import utils

from tangobenchmarks.client.python.pipe_read import Worker as ReadWorker


class ReadPipeBenchmark(utils.Benchmark):
    """  master class for pipe benchmark
    """

    def __init__(self, options):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """

        utils.Benchmark.__init__(self)
        #: (:obj:`str`) device proxy
        self.__device = options.device
        #: (:obj:`str`) device pipe name
        self.__pipe = options.pipe
        #: (:obj:`float`) time period in seconds
        self.__period = float(options.period)
        #: (:obj:`int`) number of clients
        self.__clients = int(options.clients)
        #: (:obj:`list` < :class:`multiprocessing.Queue` >) result queues
        self._qresults = [Queue() for i in range(self.__clients)]

        #: (:obj:`list` < :class:`Worker` >) process worker
        self._workers = [
            ReadWorker(i, self.__device, self.__pipe, self.__period,
                       self._qresults[i])
            for i in range(self.__clients)
        ]


def main(**kargs):
    """ the main function
    """

    parser = argparse.ArgumentParser(
        description='perform check if and how a number of simultaneous '
        'clients affect pipes pipe speed',
        formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        default=False,
        dest="version",
        help="program version")
    parser.add_argument(
        "-d", "--device", dest="device",
        help="device on which the test will be performed")
    parser.add_argument(
        "-n", "--numbers-of-clients", dest="clients", default="1",
        help="numbers of clients to be spawned separated by ',' .\n"
        "The numbers can be given as python slices <start>:<stop>:<step> ,\n"
        "e.g. 1,23,45:50:2 , default: 1")
    parser.add_argument(
        "-p", "--test-period", dest="period", default="10",
        help="time in seconds for which counting is preformed, default: 10")
    parser.add_argument(
        "-i", "--pipe", dest="pipe",
        default="BenchmarkPipe",
        help="pipe which will be read/write, default: BenchmarkPipe")
    parser.add_argument(
        "-s", "--size", dest="size",
        default="1",
        help="pipe size, default: 1, e.g. -s 134 ")
    parser.add_argument(
        "-f", "--csv-file", dest="csvfile",
        help="pipe output in a CSV file")
    parser.add_argument(
        "-t", "--title", dest="title",
        default="Pipe Benckmark",
        help="benchmark title")
    parser.add_argument(
        "--description", dest="description",
        default="Speed test",
        help="benchmark description")
    parser.add_argument(
        "--verbose", dest="verbose", action="store_true", default=False,
        help="verbose mode")

    if not kargs:
        options = parser.parse_args()
    else:
        options = parser.parse_args([])
        for ky, vl in kargs.items():
            setattr(options, ky, vl)

    clients = []

    if options.version:
        print(release.version)
        sys.exit(0)

    if not options.device:
        parser.print_help()
        print("")
        sys.exit(255)

    if not options.clients:
        options.clients = "1"
    else:
        try:
            sclients = options.clients.split(',')
            for sc in sclients:
                if ":" in sc:
                    sld = list(map(int, sc.split(":")))
                    clients.extend(list(range(*sld)))
                else:
                    clients.append(int(sc))
        except Exception:
            print("Error: number of clients is not an integer")
            parser.print_help()
            print("")
            sys.exit(255)

    if not options.period:
        options.period = "10"
    else:
        try:
            float(options.period)
        except Exception:
            print("Error: test period is not a number")
            parser.print_help()
            print("")
            sys.exit(255)

    if not options.pipe:
        options.pipe = "BenchmarkPipe"

    headers = [
        "Run no.", "No. clients",
        "Sum counts [read]", "SD [read]",
        "Sum Speed [read/s]", "SD [read/s]",
        "Counts [read]", "SD [read]",
        "Speed [read/s]", "SD [read/s]",
        "  Time [s]  ", "  SD [s]  ", " Errors "
    ]

    if options.csvfile:
        csvo = utils.CSVOutput(options.csvfile, options)
        csvo.printInfo()
        csvo.printHeader(headers)

    rst = utils.RSTOutput(options)
    rst.printInfo()
    rst.printHeader(headers)

    for i, cl in enumerate(clients):
        options.clients = cl
        bm = ReadPipeBenchmark(options=options)
        bm.start()
        bm.fetchResults(options.verbose)
        out = bm.output(False)
        record = [
            str(i), cl,
            out["sumcounts"], out["sd_sumcounts"],
            out["sumspeed"], out["sd_sumspeed"],
            out["counts"], out["sd_counts"],
            out["speed"], out["sd_speed"],
            out["time"], out["sd_time"],
            out["error_sum"]
        ]
        rst.printLine(record)
        if options.csvfile:
            csvo.printLine(record)

    rst.printEnd()

    if options.csvfile:
        csvo.printEnd()


if __name__ == "__main__":
    main()

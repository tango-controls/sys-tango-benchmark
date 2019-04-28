from multiprocessing import Queue

from . import utils

from tangobenchmarks.client.python.pipe_read import Worker as ReadWorker
from tangobenchmarks.utility.benchmark import common_main


class ReadPipeBenchmark(utils.Benchmark):
    """  master class for pipe benchmark
    """

    def __init__(self, options):
        """ constructor

        :param options: commandline options
        :type options: :class:`argparse.Namespace`
        """

        utils.Benchmark.__init__(self)
        #: (:obj:`list` < :class:`multiprocessing.Queue` >) result queues
        self._qresults = [Queue() for i in range(options.clients)]
        #: (:obj:`list` < :class:`Worker` >) process worker
        self._workers = [
            ReadWorker(i, q, options)
            for i, q in enumerate(self._qresults)
        ]


def _add_arguments(parser):
    parser.add_argument(
        "-i", "--pipe", dest="pipe",
        default="BenchmarkPipe",
        help="pipe which will be read/write, default: BenchmarkPipe")
    parser.add_argument(
        "-s", "--size", dest="size",
        default="1",
        help="pipe size, default: 1, e.g. -s 134 ")


def _update_options(options):
    if not options.pipe:
        options.pipe = "BenchmarkPipe"


def main(**kargs):
    common_main(
        kargs,
        _add_arguments,
        _update_options,
        benchmark_class=ReadPipeBenchmark,
        description=(
            'perform check if and how a number of simultaneous '
            'clients affect pipes read speed'),
        title="Pipe Read Benchmark",
        header_text="read")


if __name__ == "__main__":
    main()

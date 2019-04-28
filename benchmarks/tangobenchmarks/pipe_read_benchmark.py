from tangobenchmarks.client.python.pipe_read import Worker as ReadWorker
from tangobenchmarks.utility.benchmark import common_main


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
        worker_class=ReadWorker,
        description=(
            'perform check if and how a number of simultaneous '
            'clients affect pipes read speed'),
        title="Pipe Read Benchmark",
        header_text="read")


if __name__ == "__main__":
    main()

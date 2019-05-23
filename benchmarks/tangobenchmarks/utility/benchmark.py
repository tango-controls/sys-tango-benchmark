import sys
import argparse
import importlib

from tangobenchmarks import release
from tangobenchmarks import utils


def _load_worker(worker_class):
    try:
        module, clazz = worker_class.rsplit(".", 1)
        m = importlib.import_module(module)
        return getattr(m, clazz)
    except Exception as e:
        print(e)
        print("Cannot load worker class")
        sys.exit(255)


def common_main(
        kw_options,
        add_arguments,
        update_options,
        default_worker,
        description,
        title,
        header_text,
        build_extra_options=None):

    parser = argparse.ArgumentParser(
        description='perform check if and how a number of simultaneous '
        'clients affect attributes reads speed',
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        default=False,
        dest="version",
        help="program version")
    parser.add_argument(
        "--worker",
        dest="worker",
        help="custom worker class, e.g. my.module.MyWorker",
        default=default_worker)
    parser.add_argument(
        "--worker-program",
        dest="worker_program",
        help="path to executable program for external worker",
        default=default_worker)
    parser.add_argument(
        "-d", "--device", dest="device",
        help="device on which the test will be performed")
    parser.add_argument(
        "-n", "--numbers-of-clients", dest="clients", default="1",
        help="numbers of clients to be "
        "spawned separated by ',' .\n"
        "The numbers can be given as python "
        "slices <start>:<stop>:<step> ,\n"
        "e.g. 1,23,45:50:2 , default: 1")
    parser.add_argument(
        "-p", "--test-period", dest="period", default="10",
        help="time in seconds for which counting is preformed, "
        "default: 10")
    parser.add_argument(
        "-f", "--csv-file", dest="csvfile",
        help="write output in a CSV file")
    parser.add_argument(
        "-t", "--title", dest="title",
        default="Read Benckmark",
        help="benchmark title")
    parser.add_argument(
        "--description", dest="description",
        default="Speed test",
        help="benchmark description")
    parser.add_argument(
        "--verbose", dest="verbose", action="store_true",
        default=False,
        help="verbose mode")

    add_arguments(parser)

    if not kw_options:
        options = parser.parse_args()
    else:
        options = parser.parse_args([])
        for ky, vl in kw_options.items():
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
                    sld = [int(sl) for sl in sc.split(":")]
                    clients.extend(list(range(*sld)))
                else:
                    clients.append(int(sc))
        except Exception as e:
            print("Error: number of clients is not an integer")
            if options.verbose:
                print(str(e))
            parser.print_help()
            print("")
            sys.exit(255)

    if not options.period:
        options.period = "10"
    else:
        try:
            float(options.period)
        except Exception as e:
            print("Error: test period is not a number")
            if options.verbose:
                print(str(e))
            parser.print_help()
            print("")
            sys.exit(255)

    update_options(options)

    header_template = [
        "Run no.", "No. clients",
        "Sum counts [{0}]", "SD [{0}]",
        "Sum Speed [{0}/s]", "SD [{0}/s]",
        "Counts [{0}]", "SD [{0}]",
        "Speed [{0}/s]", "SD [{0}/s]",
        "  Time [s]  ", " SD [s]  ", " Errors "
    ]
    headers = [s.format(header_text) for s in header_template]

    if options.csvfile:
        csvo = utils.CSVOutput(options.csvfile, options)
        csvo.printInfo()
        csvo.printHeader(headers)

    rst = utils.RSTOutput(options)
    rst.printInfo()
    rst.printHeader(headers)

    options.period = float(options.period)

    if not options.worker:
        options.worker = default_worker

    extra_options = build_extra_options(options) \
        if build_extra_options else {}
    worker_class = _load_worker(options.worker)

    for i, cl in enumerate(clients):
        options.clients = int(cl)
        bm = utils.Benchmark(
            worker_class=worker_class,
            options=options,
            extra_options=extra_options)
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

import sys
import argparse

from tangobenchmarks import release
from tangobenchmarks import utils


def common_main(
        kw_options,
        add_arguments,
        update_options,
        benchmark_class,
        description,
        title,
        header_text):

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
                    sld = list(map(int, sc.split(":")))
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

    headers = list(map(lambda s: s.format(header_text), [
        "Run no.", "No. clients",
        "Sum counts [{0}]", "SD [{0}]",
        "Sum Speed [{0}/s]", "SD [{0}/s]",
        "Counts [{0}]", "SD [{0}]",
        "Speed [{0}/s]", "SD [{0}/s]",
        "  Time [s]  ", " SD [s]  ", " Errors "
    ]))

    if options.csvfile:
        csvo = utils.CSVOutput(options.csvfile, options)
        csvo.printInfo()
        csvo.printHeader(headers)

    rst = utils.RSTOutput(options)
    rst.printInfo()
    rst.printHeader(headers)

    options.period = float(options.period)

    for i, cl in enumerate(clients):
        options.clients = int(cl)
        bm = benchmark_class(options=options)
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

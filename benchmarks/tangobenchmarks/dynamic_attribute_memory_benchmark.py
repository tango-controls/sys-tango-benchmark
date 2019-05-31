#!/usr/bin/env python

import sys
import tango

from tangobenchmarks.utility.options import \
    COMMON_DEFAULT_OPTIONS, \
    DictAsObject, \
    create_common_argparser, \
    update_list_slices_option, \
    validate_common_options, \
    build_options

from tangobenchmarks.utility.benchmark import run_benchmark


OUTPUT_HEADERS = [
    "Run no.",
    "No. of attributes",
    "Used memory [B]",
    "Errors"
]


DEFAULT_OPTIONS = dict(COMMON_DEFAULT_OPTIONS, **{
    'number_of_attributes': "10",
    'spectrum_size': 100,
    'title': "Dynamic attribute memory benchmark",
    'description': "Measures dynamic attribute impact on memory consumption",
})


def create_argparser(defaults):

    parser = create_common_argparser(defaults)

    parser.add_argument(
        "-n",
        "--numbers-of-attributes",
        metavar="N",
        dest="number_of_attributes",
        default=defaults['number_of_attributes'],
        help=(
            "numbers of dynamic attributes to create, separated by ','.\n"
            "The numbers can be given as python slices "
            "<start>:<stop>:<step> ,\n"
            "e.g. 1,23,45:50:2 "
            "(default: %(default)s)"))

    parser.add_argument(
        "-s",
        "--spectrum-size",
        type=int,
        metavar="S",
        dest="spectrum_size",
        default=defaults['spectrum_size'],
        help="size of the spectrum attribute (default: %(default)s)")

    return parser


def validate_options(options):
    check, _ = validate_common_options(options)
    check('number_of_attributes', list)
    check('spectrum_size', int)


def _benchmark(options):

    try:
        proxy = tango.DeviceProxy(options.device)
        proxy.set_timeout_millis(2*60*1000)
        proxy.command_inout("ClearDynamicAttributes")
    except Exception as e:
        sys.stderr.write("{}\n".format(e))
        return

    total_num_of_attr = 0

    for (i, num_of_attr) in enumerate(options.number_of_attributes):
        delta_num_of_attr = max(0, num_of_attr - total_num_of_attr)

        args = [delta_num_of_attr, options.spectrum_size]

        min_attr_idx = total_num_of_attr
        max_attr_idx = total_num_of_attr + delta_num_of_attr

        errors = 0
        memory = 0

        try:
            res = proxy.command_inout("CreateDynamicAttributes", args)
            assert res == max_attr_idx, "Failed to create attributes"

            for n in range(min_attr_idx, max_attr_idx):
                proxy.write_attribute(
                    "BenchmarkDynamicSpectrumAttribute_{}".format(n),
                    [])
        except Exception:
            errors += 1

        try:
            memory = proxy.command_inout("GetMemoryUsage")
        except Exception:
            pass

        total_num_of_attr += delta_num_of_attr

        record = [i, total_num_of_attr, memory, errors]
        yield record

    try:
        proxy.command_inout("ClearDynamicAttributes")
    except Exception as e:
        sys.stderr.write("{}\n".format(e))
        return


def run(config):
    options = build_options(config, DEFAULT_OPTIONS)
    update_list_slices_option(options, 'number_of_attributes')
    validate_options(options)
    run_benchmark(
        benchmark=_benchmark,
        options=DictAsObject(options),
        output_headers=OUTPUT_HEADERS)


def main():
    parser = create_argparser(DEFAULT_OPTIONS)
    args = parser.parse_args()
    return run(vars(args))


if __name__ == "__main__":
    main()

#!/usr/bin/env python

import sys
import time
import tango

from tangobenchmarks.utility.options import \
    COMMON_DEFAULT_OPTIONS, \
    DictAsObject, \
    create_common_argparser, \
    update_list_slices_option, \
    validate_common_options, \
    build_options

from tangobenchmarks.utility.server_process_manager import \
    ServerProcessManager

from tangobenchmarks.utility.benchmark import run_benchmark


OUTPUT_HEADERS = [
    "Run no.",
    "No. of devices",
    "Startup time [s]",
    "Errors"
]


DEFAULT_OPTIONS = dict(COMMON_DEFAULT_OPTIONS, **{
    'number_of_devices': "10",
    'device_name_base': "test/pybenchmarktarget/dev_",
    'device_class': "PyBenchmarkTarget",
    'device_server': "PyBenchmarkTarget/rtest",
    'with_starter': False,
    'ping_last': False,
    'title': "Server startup time benchmark",
    'description': "Measures number of devices impact on server startup time",
})


def create_argparser(defaults):

    parser = create_common_argparser(defaults)

    parser.add_argument(
        "-n",
        "--numbers-of-devices",
        metavar="N",
        dest="number_of_devices",
        default=defaults['number_of_devices'],
        help=(
            "numbers of dynamic devices to create, separated by ','.\n"
            "The numbers can be given as python slices "
            "<start>:<stop>:<step> ,\n"
            "e.g. 1,23,45:50:2 "
            "(default: %(default)s)"))

    parser.add_argument(
        "--device-name-base",
        metavar="DEVICE",
        dest="device_name_base",
        default=defaults['device_name_base'],
        help=(
            "name devices like %(metavar)s_{0, ..., N} "
            "(default: %(default)s)"))

    parser.add_argument(
        "--device-class",
        metavar="CLASS",
        dest="device_class",
        default=defaults['device_class'],
        help=(
            "use %(metavar)s for device class "
            "(default: %(default)s)"))

    parser.add_argument(
        "--device-server",
        metavar="EXEC/INST",
        dest="device_server",
        default=defaults['device_server'],
        help=(
            "use %(metavar)s for device server "
            "(default: %(default)s)"))

    parser.add_argument(
        "--with-starter",
        dest="with_starter",
        action="store_true",
        default=False,
        help=(
            "use starter device to start servers"
            "(default: %(default)s)"))

    parser.add_argument(
        "--ping-last",
        dest="ping_last",
        action="store_true",
        default=False,
        help=(
            "ping last configured device server instead of admin device "
            "to determine whether the server has started. "
            "Should be used with java servers"
            "(default: %(default)s)"))

    return parser


def validate_options(options):
    check, _ = validate_common_options(options)
    check('number_of_devices', list)
    check('device_name_base', str)
    check('device_class', str)
    check('device_server', str)
    check('with_starter', bool)


def _declare_devices(db, devices, clazz, server):
    for device in devices:
        info = tango.DbDevInfo()
        info._class = clazz
        info.server = server
        info.name = device
        db.add_device(info)


def _remove_all_devices(db, name_prefix):
    devices = db.command_inout("DbGetDeviceWideList", name_prefix + '*')
    for device in devices:
        db.delete_device(device)


def _make_starter_proxy(db):
    try:
        starters = db.get_device_exported_for_class("Starter")
        return tango.DeviceProxy(starters[0])
    except Exception:
        return None


def _ping_device(proxy, timeout):
    start_time = time.time()
    end_time = start_time
    while (end_time - start_time) < timeout:
        try:
            end_time = time.time()
            proxy.ping()
            return (end_time - start_time)
        except tango.DevFailed:
            time.sleep(0.2)
    raise Exception("timeout")


def _benchmark(options):

    total_num_of_dev = 0

    db = tango.Database()
    starter = _make_starter_proxy(db)

    _remove_all_devices(db, options.device_name_base)

    try:
        starter.DevStop(options.device_server)
    except Exception:
        pass

    for (i, num_of_dev) in enumerate(options.number_of_devices):

        delta_num_of_dev = max(0, num_of_dev - total_num_of_dev)

        min_dev_idx = total_num_of_dev
        max_dev_idx = total_num_of_dev + delta_num_of_dev
        dev_idx = range(min_dev_idx, max_dev_idx)

        devices = (options.device_name_base + str(i) for i in dev_idx)

        _declare_devices(
            db,
            devices,
            options.device_class,
            options.device_server)

        with ServerProcessManager(
                options.device_server,
                starter if options.with_starter else None) as admin:

            startup_time = 0
            errors = 0

            if options.ping_last:
                last_dev_name = options.device_name_base + str(max_dev_idx - 1)
                dev_to_ping = tango.DeviceProxy(last_dev_name)
            else:
                dev_to_ping = admin

            try:
                startup_time = _ping_device(dev_to_ping, timeout=2*60)
            except Exception:
                errors = 1

            total_num_of_dev += delta_num_of_dev

            record = [i, total_num_of_dev, startup_time, errors]
            yield record

    _remove_all_devices(db, options.device_name_base)


def run(config):
    options = build_options(config, DEFAULT_OPTIONS)
    update_list_slices_option(options, 'number_of_devices')
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

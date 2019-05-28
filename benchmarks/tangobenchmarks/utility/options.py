
import argparse
import tangobenchmarks.release


COMMON_DEFAULT_OPTIONS = {
    'verbose': False,
    'csvfile': None
}


class DictAsObject(object):
    def __init__(self, d):
        self.__dict__ = d


def create_common_argparser(defaults):

    parser = argparse.ArgumentParser(
        description=defaults['description'],
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {}".format(tangobenchmarks.release.version))

    parser.add_argument(
        "-d",
        "--device",
        dest="device",
        required=True,
        help="target device")

    csvfile_arg = parser.add_argument(
        "-f",
        "--csv-file",
        dest="csvfile",
        help="write CSV output to %(metavar)s")

    if csvfile_arg.metavar is None:
        csvfile_arg.metavar = csvfile_arg.dest.upper()

    parser.add_argument(
        "-t",
        "--title",
        dest="title",
        default=defaults['title'],
        help="benchmark title")

    parser.add_argument(
        "--description",
        dest="description",
        default=defaults['description'],
        help="benchmark description")

    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="enable verbose mode")

    return parser


def build_list_from_slices(text):
    data = []
    for entry in text.split(','):
        if ":" in entry:
            list_args = list(map(int, entry.split(":")))
            data.extend(list(range(*list_args)))
        else:
            data.append(int(entry))
    return data


def update_list_slices_option(options, key):
    assert key in options, "{} option must be provided".format(key)
    slices = options[key]
    try:
        value = build_list_from_slices(slices)
        options[key] = value
    except:
        assert False, "{} option has incorrect value {}".format(key, slices)


def validate_common_options(options):

    def check(key, tpe):
        assert (key in options) and type(options[key]) is tpe, \
            "{} option must be of type {}".format(key, tpe)

    def check_opt(key, tpe):
        assert (key in options) and type(options[key]) in [tpe, type(None)], \
            "{} option must be of type {}".format(key, tpe)

    check('device', str)
    check('title', str)
    check('description', str)
    check('verbose', bool)
    check_opt('csvfile', str)

    return (check, check_opt)


def build_options(options, defaults):
    new_options = defaults.copy()
    new_options.update(options)
    return new_options

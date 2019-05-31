
from tangobenchmarks.utils import CSVOutput, RSTOutput


class BenchmarkOutputWriter(object):

    def __init__(self, csv, rst):
        self.__csv = csv
        self.__rst = rst

    def print_line(self, record):
        if self.__csv:
            self.__csv.printLine(record)
        if self.__rst:
            self.__rst.printLine(record)


class BenchmarkOutputManager(object):

    def __init__(self, headers, options):
        self.__headers = headers
        self.__options = options
        self.__csv = None
        self.__rst = None

    def __enter__(self):

        if self.__options.csvfile:
            self.__csv = CSVOutput(self.__options.csvfile, self.__options)
            self.__csv.printInfo()
            self.__csv.printHeader(self.__headers)

        self.__rst = RSTOutput(self.__options)
        self.__rst.printInfo()
        self.__rst.printHeader(self.__headers)

        return BenchmarkOutputWriter(self.__csv, self.__rst)

    def __exit__(self, *args):
        self.__rst.printEnd()
        if self.__options.csvfile:
            self.__csv.printEnd()

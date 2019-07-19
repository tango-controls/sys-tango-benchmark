import os
import sys
import subprocess
import multiprocessing

import tangobenchmarks.utils as utils


class Worker(multiprocessing.Process):

    def __init__(self, wid, qresult, options, **_):
        multiprocessing.Process.__init__(self)
        self.__wid = wid
        self.__qresult = qresult
        self.__options = options

    def _build_env(self):
        env = os.environ.copy()
        for k, v in vars(self.__options).items():
            env["_TANGO_BENCHMARK_" + k] = str(v)
        return env

    def _build_result(self, output):
        counter, time, errors = output.split()
        return utils.Result(
            self.__wid,
            int(counter),
            float(time),
            int(errors))

    def _parse_output(self, output_lines):
        for line in output_lines.splitlines():
            try:
                return self._build_result(line)
            except Exception:
                pass
        sys.stderr.write(
            "Malformed result from external client: %s\n" % output_lines)
        return utils.Result(self.__wid, 0, 0, 0)

    def _start(self):
        self.__process = subprocess.Popen(
            [self.__options.worker_program],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._build_env())

    def _join(self):
        out, err = self.__process.communicate()
        self.__qresult.put(self._parse_output(out))
        if err:
            sys.stderr.write(err + "\n")

    def run(self):
        self._start()
        self._join()

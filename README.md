# sys-tango-benchmark
[![Build Status](https://travis-ci.org/tango-controls/sys-tango-benchmark.svg?branch=master)](https://travis-ci.org/tango-controls/sys-tango-benchmark)

A Tango Controls Benchmark suite

This is a set of tools to test impact of various deployment qualities (like number of concurrent conncetions) on a tango system efficiency. 

The suit consists of the following componets:

1) Target device servers providing C++, Java and Python device classes. These device classes provide mocking interface along with counting facility (to measure operations).

2) Set of benchmark scripts. These scripts run specific benchmark tests and produce output both in reStructuredText (to stdout) and in CSV. 

3) Benchmark runner (in developement). It is a tool for setting up environment and running a set of benchmarks defined in a config file.

4) Benchpar report geretor which gather outputs from benchmarks and produce a PDF with data and plots.

5) Docker images (to be provided) for rapid benchmark deployment.


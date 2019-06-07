## sys-tango-benchmark
[![Build Status](https://travis-ci.org/tango-controls/sys-tango-benchmark.svg?branch=master)](https://travis-ci.org/tango-controls/sys-tango-benchmark)

# A Tango Controls Benchmark suite

This is a set of tools to test impact of various deployment qualities (like number of concurrent connections) 
on a tango system efficiency. 

The suite consists of the following components:

1. Target device servers, which are providing C++, Java and Python device classes. These device classes provide 
   mocking interface along with counting facility (to measure operations).

2. Set of benchmark scripts. These scripts run specific benchmark tests and produce 
   output in reStructuredText (to stdout) and in CSV format to a file if requested. 

3. A benchmark runner. It is a tool for setting up an environment 
   and running a set of benchmarks defined in a config file.

4. Benchmark report generator (planned) which will gather outputs from benchmarks and produce a PDF with data and plots.

5. Docker images (to be provided) for rapid benchmark deployment.

## Quick start (running everything locally)

### Prerequisites

To use the benchmark you need:

Properly configured and running a Tango Controls system. 

For server side:
- Tango Java libraries, to benchmark Java device server, 
- PyTango, to test PyTango device servers,
- CppTango, to run tests with C++ device server.

For client side (benchmark runners):
- PyTango and its dependencies.

### Installation:

1. clone the repository: `git clone https://github.com/tango-controls/sys-tango-benchmark`

1. change to the cloned folder `cd sys-tango-benchmark`

1. install device servers from `ds` folder:

    - the Python target
        - `cd ds/PyBenchmarkTarget`
        - `pip install .`
    - the C++ target
        - `cd ../CppBenchmarkTarget`
        - `make`
        - `sudo -E make install`
    - the Java target
        - `cd ../JavaBenchmarkTarget`
        - `mvn clean install`
        - Copy the startup script to where it can be found by the Starter:
            - `sudo cp src/scripts/JavaBenchmarkTarget /usr/local/bin/`
        - Copy the compiled jar file to `$TANGO_ROOT/share/java/`:
            - `sudo cp target/JavaBenchmarkTarget-1.0.jar /usr/local/share/java/`

1. Make sure that the installed device servers are in *Starter* paths (if you use Starter) or in *PATH*. 
   The benchmark runner will try to either run the servers with the *Starter* service or as command line processes.

1. Install benchmarks from `benchmarks` folder. 
    - Go to this folder: `cd benchmarks`
    - Install: `pip install .`

1. Install C++ workers:
    ```bash
    cd cppclient
    make all
    sudo -E make install
    # or make install INSTALL_DIR=~/.local/bin
    ```

1. Install Java workers:
    ```bash
    cd javaclient
    for d in tg-benchmark-client-*; do cd $d && mvn package; cd ..; done
    sudo cp -f tg-benchmark-client-*/target/*.jar ${TANGO_ROOT:-/usr}/share/java
    sudo bash -c $'for d in tg-benchmark-client-*; do client=$(echo $d | awk -F- \'{print $NF}\') && outfile=${TANGO_ROOT:-/usr}/bin/tg_benchmark_client_java_$client && cat script-template | sed "s/^CLIENT=$/CLIENT=$client/g" > $outfile && chmod +x $outfile; done'
    ```

### Running a default benchmark

The benchmark runner (`tg_benchmarkrunner`) uses a configuration script provided with `-c` command line options. 
The suite comes with set of preconfigured tests (see the *benchmarks/config_examples* folder). 
- Go to the examples folder: `cd benchmarks/config_examples`
- Run the benchmark: `tg_benchmarkrunner -c default.yml`

Please look on/run with other config files, too. To use a `python_heavy.json` example
configuration you may need to increase a limit of opened files (`ulimit -n 2048`).

### Output

Benchmarks write results to the stdout as reStructuredText 
and optionally to a CSV file  (if requested with `--csv-file` option).
The output contains configuration parameters and a result table. 

Below is a description of certain columns of the result table:
- `Run no.`:  subsequent run (with new input parameters, usually new number of clients),
- `Sum counts`: total number of operations (reads, writes, subscriptions etc., depending of type of benchmark)
  counted during period (`Time`) of the run,
- `Sum speed`: `Sum counts`/`Time`, how fast certain operation can be performed on server side,
- `Counts`: average number of benchmarked operations within one client, `Sum counts`/`No. clients`,
- `Speed`: average speed of clients, `Counts`/`Time`,
- `No. clients`: number of clients for this run,
- `Time`: Measured period of the run, 
- `Errors`: communication errors are counted during period of measurement,
- `SD`: columns contains standard deviation of a related values. These may be used as indicators of validity of benchmark.

**Hint:** You may generate a pdf file from benchmark results with `rst2pdf`: 
- Install it if not installed: `pip isntall rst2pdf`,
- Run a benchmark like the following: `tg_benchmarkrunner -c default.yml | rst2pdf -o benchmark-result.pdf`.

## Remarks

### Available benchmarks

You may run an individual benchmark from a command line. Each benchmark accepts set of command-line parameters
to define a scope of tests. Please use `--help` option to list them. Below is a list of available benchmarks. 

- `tg_commandbenchmark` performs check if and how a number of simultaneous clients affects command calls speed,
- `tg_readbenchmark` checks how the number of clients affects attributes read speed. One may chose whether 
   it reads scalar, spectrum or image attribute,
- `tg_writebenchmark` checks how the number of clients affects attributes write speed. One may chose whether 
   it reads scalar, spectrum or image attribute,
- `tg_pipe_read_benchmark` checks how number of clients affects pipe read speed. Size of pipe may be provided to check 
  also impact of data size,
- `tg_pipe_write_benchmark` checks how number of clients affects pipe write speed. Size of pipe may be provided to check 
  also impact of data size,
- `tg_eventbanchmark` checks how event subscription time is affected by number of clients.

Please note, new ones will be provided soon :).

### Target devices

However a set of target devices is provided, a benchmarks may be run against any device providing suitable
interface (for example, benchmark using an attribute needs a device exposing at least one attribute). 
The target device name and a subject *attribute* or *command* or *pipe* is configured either in 
a *configuration file* for the runner or as a command-line options for individual benchmark scripts.

### The benchmark runner

The benchmark runner reads a configuration file and run set of benchmarks defined in it. 

To simplify performing of tests an auto-setup is implemented. The runner first checks if target devices are on-line.
If these are not running it makes attempt to configure the missing devices in the tango database.
Then it tries to run them with the *Starter* or from the command line. 

The configuration file allows to define a machine (`host` parameter) on which the certain target device should be run. 
For remote machines, the auto-setup feature requires them to run a *Starter* device. Of course, the target device servers
should be installed on that machine and available to the *Starter*.

#### Configuration file

The benchmark runner reads a JSON or YML configuration file and based on it, it runs benchmarks with 
prior attempt to prepare an environment (configure tango database and start a missing devices).

The file is a list of items corresponding to benchmarks to be run as the following (in case of JSON):
```json
[
    {
      benchmark: name_of_the_benchmark_script
      commandline_param1_name: commandline_param1_value
      ....
      commandline_paramN_name: commandline_paramN_value
    },
]
```
And optionally spec for environment setup (target devices):

```json
[
    {
      target_device: name_of_device
      device_class: CppBenchmarkTarget or JavaBenchmarkTarget or PythonBenchmarkTarget or TangoTest
      server_instance: name_of_server_instance 
      host: name_of_host_where_the_device_should_be_run  #used only if there is a Starter device running, if not provided default is local
    } 
]
```

See, a YAML example:

```yaml
- benchmark: readbenchmark
  title: "java read benchmark"
  clients: 4,6,8,10
  device: test/javabenchmarktarget/01
  period: 1

- benchmark: writebenchmark
  title: "java write benchmark"
  clients: 4,6,8,10
  device: test/javabenchmarktarget/01
  period: 1

- benchmark: eventbenchmark
  title: "java event benchmark"
  clients: 4,6,8,10
  device: test/javabenchmarktarget/01
  period: 1

- benchmark: pipebenchmark
  title: "java pipe benchmark"
  clients: 4,6,8,10
  device: test/javabenchmarktarget/01
  period: 1


- server_instance: JavaBenchmarkTarget/rtest
  device_class: JavaBenchmarkTarget
  target_device: test/javabenchmarktarget/01
  # host: localhost:10000
```

#### Custom workers

It is possible to use a custom worker (client) class in order to change the test
scenario or tweak some parameters. Option `worker` (or `--worker` argument)
must point to a worker module/class, e.g.:
```yaml
- benchmark: readbenchmark
  title: "benchmark with custom worker"
  clients: 4,6,8,10
  device: test/pybenchmarktarget/01
  period: 1
  worker: your.custom.WorkerClass
```

In the example above, `WorkerClass` is located in `your.custom` module on `$PYTHONPATH`.

The worker class must expose `multiprocessing.Process`-like interface, e.g.:
```python
class WorkerClass
    def __init__(self, wid, qresult, options, **_):
        pass

    def start(self):
        pass

    def join(self):
        pass
```

Where:
* `wid` is worker id (`int`),
* `qresult` is a `multiprocessing.Queue` and must be populated with
  `tangobenchmarks.utils.Result`
* `options` is a dictionary with configuration file entries
  (or commandline arguments)

If no `worker` is configured, a default worker (specific to each benchmark)
is used.

#### Workers in external programs

`tangobenchmarks.client.external.Worker` module allows to use an external program
as a benchmark worker. `worker_program` option (or `--worker-program` argument)
must point to the worker program. It is possible to use either an absolute path,
a relative path (to benchmark's working directory) or a name available on `$PATH`.
```yaml
- benchmark: writebenchmark
  # ...
  worker: tangobenchmarks.client.external.Worker
  worker_program: "test/assets/dummy_client.sh"
```

All benchmark options are passed to the worker program via environment
variables. Variable names are prefixed with `_TANGO_BENCHMARK_`. Example
variable names are:
* `_TANGO_BENCHMARK_device`
* `_TANGO_BENCHMARK_period`

Worker program is expected to print a single line to stdandard output and then
exit with 0. The output must be formatted as follows:

```
<number-of-successful-operations> <time-delta> <number-of-errors>
```

#### C++ workers

Some C++ workers are provided as an alternative to default Python workers.
C++ workers are located in `cppclient` directory. The workers need to be
compiled, e.g. using provided `Makefile`:

```bash
cd cppclient
make all
make install INSTALL_DIR=~/.local/bin
# or: sudo -E make install
```

C++ worker program must be configured using external worker module, e.g.:
```yaml
- benchmark: readbenchmark
  # ...
  worker: tangobenchmarks.client.external.Worker
  worker_program: path/to/cppclient/bin/tg_benchmark_client_read
```

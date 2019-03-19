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

2. change to the cloned folder `cd sys-tango-benchmark`

3. install device servers from `ds` folder:

    - the Python target
        - `cd ds/PyBenchmarkTarget`
        - `pip install .`
    - the C++ target
        - `cd ../CppBenchmarkTarget`
        - `make`
        - `sudo make install`
    - the Java target
        - `cd ../JavaBenchmarkTarget`
        - `mvn clean install`
        - Copy the startup script to where it can be found by the Starter:
            - `sudo cp src/scripts/JavaBenchmarkTarget /usr/local/bin/`
        - Copy the compiled jar file to `$TANGO_ROOT/share/java/`:
            - `sudo cp target/JavaBenchmarkTarget-1.0.jar /usr/local/share/java/`


4. Make sure that the installed device servers are in *Starter* paths (if you use Starter) or in *PATH*. 
   The benchmark runner will try to either run the servers with the *Starter* service or as command line processes.
      
5. Install benchmarks from `benchmarks` folder. 
    - Go to this folder: `cd benchmarks`
    - Install: `pip install .`
 
### Running a default benchmark

The benchmark runner (`tg_benchmarkrunner`) uses a configuration script provided with `-c` command line options. 
The suite comes with set of preconfigured tests (see the *benchmarks/config_examples* folder). 
- Go to the examples folder: `cd benchmarks/config_examples`
- Run the benchmark: `tg_benchmarkrunner -c default.yml`

Please look on/run with other config files, too. To use a `python_heavy.json` example
configuration you may need to increase a limit of opened files (`ulimit -n 2048`).

## Remarks

### Available benchmarks

You may run an individual benchmark from a command line. Each benchmark accepts set of command-line parameters
to define a scope of tests. Please use `--help` option to list them. Below is a list of available benchmarks. 

- `tg_commandbenchmark` performs check if and how a number of simultaneous clients affects command calls speed,
- `tg_readbenchmark` checks how the number of clients affects attributes read speed. One may chose whether 
   it reads scalar, spectrum or image attribute,
- `tg_writebenchmark` checks how the number of clients affects attributes write speed. One may chose whether 
   it reads scalar, spectrum or image attribute,
- `tg_pipebenchmark` checks how number of clients affects pipe read speed. Size of pipe may be provided to check 
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
{
  benchmark: name_of_the_benchmark_script
  commandline_param1_name: commandline_param1_value
  ....
  commandline_paramN_name: commandline_paramN_value
}
```
And optionally spec for environment setup (target devices):

```json
{
  target_device: name_of_device
  device_class: CppBenchmarkTarget or JavaBenchmarkTarget or PythonBenchmarkTarget or TangoTest
  server_instance: name_of_server_instance 
  host: name_of_host_where_the_device_should_be_run  #used only if there is a Starter device running, if not provided default is local
}
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
 

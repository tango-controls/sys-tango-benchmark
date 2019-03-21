#!/usr/bin/env bash

echo "Restarting mysql ..."
export DEBIAN_FRONTEND=noninteractive
service mysql restart

echo "Installing tango ..."
apt-get -qq update > /dev/null
apt-get install -qq tango-db tango-common tango-starter tango-test libtango-dev liblog4tango-dev libtango-tools python-pytango > /dev/null

service tango-db restart
service tango-starter restart

# apt-get -qq install -y   python-pytango

. /etc/tangorc; export TANGO_HOST;python -c "import tango;tango.Database().put_property(\"CtrlSystem\",{\"EventBufferHwm\":1000})"


cd /opt ;
dpkg -i ./libtango-java_9.2.5a-1_all.deb > /dev/null

echo "Installing CppBenchmarkTarget ..."
cd /opt/sys-tango-benchmark/ds/CppBenchmarkTarget
make -s > /dev/null 2> /dev/null
make install -s > /dev/null 2> /dev/null

echo "Installing JavaBenchmarkTarget ..."
cd /opt/sys-tango-benchmark/ds/JavaBenchmarkTarget
mvn clean install -q > /dev/null 2> /dev/null
cp src/scripts/JavaBenchmarkTarget /usr/bin/
cp target/JavaBenchmarkTarget-1.0.jar /usr/share/java/
export TANGO_ROOT=/usr

# update-alternatives --list java
update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java > /dev/null

cd /opt/sys-tango-benchmark/ds/PyBenchmarkTarget; python setup.py -q install
cp -r /opt/sys-tango-benchmark/benchmarks/config_examples/* /var/lib/tango/config_examples/

chown -R tango:tango /opt/
chown -R tango:tango /opt/sys-tango-benchmark/benchmarks
chown -R tango:tango /var/lib/tango/config_examples/*

echo "Installing benchmark runner ..."
cd /opt/sys-tango-benchmark/benchmarks
sed -i 's/config_examples\//\/var\/lib\/tango\/config_examples\//g' benchmarks/runner.py
python setup.py -q install

# cd /opt/sys-tango-benchmark/benchmarks
# python setup.py test
echo "Starting: PyBenchmarkTarget/pytarget1     - sys/benchmark/pytarget01"
echo "          CppBenchmarkTarget/cpptarget1   - sys/benchmark/cpptarget01"
echo "          JavaBenchmarkTarget/javatarget1 - sys/benchmark/javatarget01"
cd /home/tango
su -s /bin/bash -c "tg_benchmarkrunner -c /var/lib/tango/config_examples/devices.json " -g tango tango > /dev/null
echo "TANGO_HOST=$TANGO_HOST"
su -s /bin/bash -g tango tango

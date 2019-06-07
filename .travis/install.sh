#!/usr/bin/env bash

# workaround for incomatibility of default ubuntu 16.04 and tango configuration
if [ "$1" = "ubuntu16.04" ]; then
    docker exec -it --user root s2i sed -i "s/\[mysqld\]/\[mysqld\]\nsql_mode = NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION/g" /etc/mysql/mysql.conf.d/mysqld.cnf
fi

docker exec -it --user root s2i service mysql stop
docker exec -it --user root s2i /bin/sh -c '$(service mysql start &) && sleep 30'

set -e

docker exec -it --user root s2i /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y tango-db tango-common; sleep 10'

echo "install tango servers"
docker exec -it --user root s2i /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get  install -y tango-starter tango-test liblog4j1.2-java g++ openjdk-8-jdk openjdk-8-jre  libtango-dev liblog4tango-dev maven maven-debian-helper maven-repo-helper dpkg'

set +e

docker exec -it --user root s2i service tango-db restart
docker exec -it --user root s2i service tango-starter restart

set -e

if [ "$2" = "2" ]; then
    echo "install python-pytango"
    docker exec -it --user root s2i /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python-pytango python-tz python-setuptools python-sphinx python-whichcraft python-yaml python-docutils python-dateutil'
else
    echo "install python3-pytango"
    docker exec -it --user root s2i /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python3-pytango python3-tz python3-setuptools python3-sphinx python3-whichcraft python3-yaml python3-docutils python3-dateutil'
fi

if [ "$2" = "2" ]; then
    echo "install python-pytango"
    docker exec -it --user root s2i /bin/sh -c '. /etc/tangorc; export TANGO_HOST;python -c "import tango;tango.Database().put_property(\"CtrlSystem\",{\"EventBufferHwm\":1000})"'
else
    echo "install python-pytango"
    docker exec -it --user root s2i /bin/sh -c '. /etc/tangorc; export TANGO_HOST;python3 -c "import tango;tango.Database().put_property(\"CtrlSystem\",{\"EventBufferHwm\":1000})"'
fi

docker exec -it --user root s2i /bin/sh -c 'curl -O https://people.debian.org/~picca/libtango-java_9.2.5a-1_all.deb; dpkg -i ./libtango-java_9.2.5a-1_all.deb'

echo "install CppBenchmarkTarget"
docker exec -it --user root s2i /bin/sh -c 'cd ds/CppBenchmarkTarget; make clean; make'

echo "install JavaBenchmarkTarget"
docker exec -it --user root s2i /bin/sh -c 'cd ds/JavaBenchmarkTarget; mvn clean install'

set +e

docker exec -it --user root s2i /bin/sh -c 'update-alternatives --list java'

set -e

docker exec -it --user root s2i /bin/sh -c 'update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java'

echo "install PyBenchmarkTarget"
if [ "$2" = "2" ]; then
    docker exec -it --user root s2i /bin/sh -c 'cd ds/PyBenchmarkTarget; python setup.py -q install'
else
    docker exec -it --user root s2i /bin/sh -c 'cd ds/PyBenchmarkTarget; python3 setup.py -q install'
fi

docker exec -it --user root s2i chown -R tango:tango .

docker exec -it --user root s2i chown -R tango:tango benchmarks

echo "install benchmark runner"
if [ "$2" = "2" ]; then
    docker exec -it --user root s2i /bin/sh -c 'cd benchmarks; python setup.py -q install'
else
    docker exec -it --user root s2i /bin/sh -c 'cd benchmarks; python3 setup.py -q install'
fi

echo "install cpp clients"
docker exec -it --user root s2i /bin/sh -c 'cd cppclient && make all'

echo "install java clients"
docker exec -it --user root s2i /bin/sh -c 'cd javaclient; for d in tg-benchmark-client-*; do cd $d && mvn package; cd ..; done'
docker exec -it --user root s2i /bin/sh -c 'cd javaclient; cp -f tg-benchmark-client-*/target/*.jar ${TANGO_ROOT:-/usr}/share/java'
docker exec -it --user root s2i /bin/sh -c $'cd javaclient; for d in tg-benchmark-client-*; do client=$(echo $d | awk -F- \'{print $NF}\') && outfile=${TANGO_ROOT:-/usr}/bin/tg_benchmark_client_java_$client && cat script-template | sed "s/^CLIENT=$/CLIENT=$client/g" > $outfile && chmod +x $outfile; done'

#!/usr/bin/env bash

# workaround for incomatibility of default ubuntu 16.04 and tango configuration
if [ "$1" = "ubuntu16.04" ]; then
    docker exec -it --user root s2i sed -i "s/\[mysqld\]/\[mysqld\]\nsql_mode = NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION/g" /etc/mysql/mysql.conf.d/mysqld.cnf
fi

docker exec -it --user root s2i service mysql stop
docker exec -it --user root s2i /bin/sh -c '$(service mysql start &) && sleep 30'

docker exec -it --user root s2i /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y tango-db tango-common; sleep 10'
if [ "$?" -ne "0" ]
then
    exit -1
fi
echo "install tango servers"
docker exec -it --user root s2i /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive;  apt-get -qq update; apt-get -qq install -y tango-starter tango-test liblog4j1.2-java g++ openjdk-8-jdk openjdk-8-jre  libtango-dev liblog4tango-dev maven maven-debian-helper maven-repo-helper dpkg'
if [ "$?" -ne "0" ]
then
    exit -1
fi

docker exec -it --user root s2i service tango-db restart
docker exec -it --user root s2i service tango-starter restart

if [ "$2" = "2" ]; then
    echo "install python-pytango"
    docker exec -it --user root s2i /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python-pytango python-tz python-setuptools python-sphinx python-whichcraft python-yaml python-docutils python-dateutil'
else
    echo "install python3-pytango"
    docker exec -it --user root s2i /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y   python3-pytango python3-tz python3-setuptools python3-sphinx python3-whichcraft python3-yaml python3-docutils python3-dateutil'
fi
if [ "$?" -ne "0" ]
then
    exit -1
fi


if [ "$2" = "2" ]; then
    echo "install python-pytango"
    docker exec -it --user root s2i /bin/sh -c '. /etc/tangorc; export TANGO_HOST;python -c "import PyTango;PyTango.Database().put_property(\"CtrlSystem\",{\"EventBufferHwm\":1000})"'
else
    echo "install python-pytango"
    docker exec -it --user root s2i /bin/sh -c '. /etc/tangorc; export TANGO_HOST;python3 -c "import PyTango;PyTango.Database().put_property(\"CtrlSystem\",{\"EventBufferHwm\":1000})"'
fi
if [ "$?" -ne "0" ]
then
    exit -1
fi


docker exec -it --user root s2i /bin/sh -c 'curl -O https://people.debian.org/~picca/libtango-java_9.2.5a-1_all.deb; dpkg -i ./libtango-java_9.2.5a-1_all.deb'
if [ "$?" -ne "0" ]
then
    exit -1
fi
echo "install CppBenchmarkTarget"
docker exec -it --user root s2i /bin/sh -c 'cd ds/CppBenchmarkTarget; make'
if [ "$?" -ne "0" ]
then
    exit -1
fi
echo "install JavaBenchmarkTarget"
docker exec -it --user root s2i /bin/sh -c 'cd ds/JavaBenchmarkTarget; mvn clean install'
if [ "$?" -ne "0" ]
then
    exit -1
fi
docker exec -it --user root s2i /bin/sh -c 'update-alternatives --list java'
docker exec -it --user root s2i /bin/sh -c 'update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java'
if [ "$?" -ne "0" ]
then
    exit -1
fi

echo "install PyBenchmarkTarget"
if [ "$2" = "2" ]; then
    docker exec -it --user root s2i /bin/sh -c 'cd ds/PyBenchmarkTarget; python setup.py -q install'
else
    docker exec -it --user root s2i /bin/sh -c 'cd ds/PyBenchmarkTarget; python3 setup.py -q install'
fi
if [ "$?" -ne "0" ]
then
    exit -1
fi

echo "install benchmark runner"
if [ "$2" = "2" ]; then
    docker exec -it --user root s2i /bin/sh -c 'cd benchmarks; python setup.py -q install'
else
    docker exec -it --user root s2i /bin/sh -c 'cd benchmarks; python3 setup.py -q install'
fi
if [ "$?" -ne "0" ]
then
    exit -1
fi


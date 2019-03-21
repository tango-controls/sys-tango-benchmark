FROM debian:buster

MAINTAINER Jan Kotanski <jankotan@gmail.com>
RUN /bin/bash -c 'echo "deb http://ftp.de.debian.org/debian buster main" > /etc/apt/sources.list.d/debian9de.list'
RUN apt-get -qq update && apt-get -qq install -y libterm-readline-gnu-perl software-properties-common coreutils gnupg2 procps apt-utils curl apt-transport-https gnupg2 ca-certificates
RUN apt-get -qq update && apt-get -qq -y dist-upgrade
RUN apt-get -qq update && apt-get -qq install -y default-mysql-client  python-sphinx  apt-utils debconf-utils net-tools  omniidl libomniorb4-dev libcos4-dev libomnithread4-dev libzmq3-dev python-mysqldb
RUN useradd -ms /bin/bash tango
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "mysql-server mysql-server/root_password password rootpw"'
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "mysql-server mysql-server/root_password_again password rootpw"'
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "mariadb-server mysql-server/root_password password rootpw"'
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "mariadb-server mysql-server/root_password_again password rootpw"'
RUN  /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-get-selections |grep mysql '
RUN apt-get -qq install -y default-mysql-server adduser
RUN  /bin/bash -c 'sleep 10'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/db/app-user string tango"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/mysql/app-pass	password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/mysql/admin-pass password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/password-confirm password rootpw"'
RUN /bin/bash -c 'export DEBIAN_FRONTEND=noninteractive; debconf-set-selections <<< "tango-db tango-db/app-password-confirm password rootpw"'

ENV PKG_CONFIG_PATH=/home/tango/lib/pkgconfig
###############################################
RUN  apt-get -qq update && apt-get -qq install -y  liblog4j1.2-java g++ openjdk-8-jdk openjdk-8-jre  maven maven-debian-helper maven-repo-helper dpkg
RUN export DEBIAN_FRONTEND=noninteractive && apt-get -qq update && apt-get -qq install -y  python-tz python-setuptools python-sphinx python-whichcraft python-yaml python-docutils python-dateutil
RUN export DEBIAN_FRONTEND=noninteractive && apt-get -qq update && apt-get -qq install -y  git dbconfig-common dbconfig-mysql libgfortran5 libblas3 python-numpy liblapack3 libboost-python1.67.0
RUN /bin/sh -c 'mkdir -p /opt'
RUN /bin/sh -c 'cd /opt && curl  -O https://people.debian.org/~picca/libtango-java_9.2.5a-1_all.deb'
RUN /bin/sh -c 'cd /opt && git clone https://github.com/tango-controls/sys-tango-benchmark'
# --download-only

RUN  apt-get -qq update && apt-get -qq install --download-only tango-db tango-common tango-starter tango-test  libtango-dev liblog4tango-dev python-pytango
RUN  /bin/sh -c 'cd /opt/sys-tango-benchmark/ds/JavaBenchmarkTarget; mvn clean install'
RUN service mysql restart

##########################################

# USER tango
WORKDIR /home/tango
RUN /bin/sh -c 'mkdir -p /var/lib/tango/config_examples'
COPY devices.json /var/lib/tango/config_examples
COPY dsstarter.sh /opt/
RUN /bin/sh -c 'chown -R tango:tango /var/lib/tango/config_examples'
RUN /bin/sh -c 'chown -R tango:tango /var/lib/tango/config_examples/devices.json'

CMD /opt/dsstarter.sh

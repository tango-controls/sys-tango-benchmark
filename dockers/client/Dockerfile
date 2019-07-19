FROM debian:buster

MAINTAINER Jan Kotanski <jankotan@gmail.com>
RUN /bin/bash -c 'echo "deb http://ftp.de.debian.org/debian buster main" > /etc/apt/sources.list.d/debian9de.list'
RUN apt-get -qq update && apt-get -qq install -y libterm-readline-gnu-perl software-properties-common coreutils gnupg2 procps apt-utils curl apt-transport-https gnupg2 ca-certificates
RUN apt-get -qq update && apt-get -qq -y dist-upgrade
RUN /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y python-pytango git libgfortran5 libblas3 python-numpy liblapack3 libboost-python1.67.0 python-tz python-setuptools python-sphinx python-whichcraft python-yaml python-docutils python-dateutil'
RUN /bin/sh -c 'export DEBIAN_FRONTEND=noninteractive; apt-get -qq update; apt-get -qq install -y openssh-client ssh ipython libzmq-java'

RUN apt update \
 && apt install -y \
    wget \
    g++ \
    binutils \
    libtango-dev

RUN mkdir tangotmp \
 && cd tangotmp \
 && wget https://people.debian.org/~picca/libtango-java_9.2.5a-1_all.deb \
 && ar x libtango-java_*.deb \
 && tar xf data.tar.xz \
 && cp -r usr/share/pogo /usr/share/ \
 && cd .. \
 && rm -rf tangotmp

RUN /bin/sh -c 'cd /opt &&  git clone https://github.com/tango-controls/sys-tango-benchmark'

RUN cd /opt/sys-tango-benchmark/cppclient \
 && make \
 && make install

RUN echo '\
deb http://snapshot.debian.org/archive/debian/20190326T120000Z buster main \n\
deb http://snapshot.debian.org/archive/debian-security/20190326T120000Z buster/updates main \n\
deb http://snapshot.debian.org/archive/debian/20190326T120000Z buster-updates main' \
> /etc/apt/sources.list

RUN apt -o Acquire::Check-Valid-Until=false update \
 && apt install -y openjdk-8-jre openjdk-8-jdk liblog4j1.2-java libzmq-java maven

RUN update-java-alternatives --set java-1.8.0-openjdk-amd64

RUN cd /opt \
 && curl -O https://people.debian.org/~picca/libtango-java_9.2.5a-1_all.deb \
 && dpkg -i ./libtango-java_9.2.5a-1_all.deb \
 && rm libtango-java_9.2.5a-1_all.deb

RUN /opt/sys-tango-benchmark/javaclient/javaclient-build.sh \
 && /opt/sys-tango-benchmark/javaclient/javaclient-install.sh

# ##########################################

WORKDIR /home/tango
RUN /bin/sh -c 'mkdir -p /var/lib/tango/config_examples'
RUN /bin/sh -c 'chown -R tango:tango /var/lib/tango/config_examples'
RUN cp -r /opt/sys-tango-benchmark/benchmarks/config_examples/* /var/lib/tango/config_examples/
RUN /bin/sh -c 'chown -R tango:tango /var/lib/tango/config_examples/*'
RUN sed -i 's/config_examples\//\/var\/lib\/tango\/config_examples\//g' /opt/sys-tango-benchmark/benchmarks/tangobenchmarks/runner.py
RUN /bin/sh -c 'cd /opt/sys-tango-benchmark/benchmarks; python setup.py -q install'

COPY clientstarter.sh /opt/
COPY waitfordevice.py /opt/
RUN /bin/sh -c 'chown -R tango:tango /opt/clientstarter.sh'
RUN /bin/sh -c 'chown -R tango:tango /opt/waitfordevice.py'

USER tango

ENTRYPOINT ["/opt/clientstarter.sh"]

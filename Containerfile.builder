FROM quay.io/centos/centos:stream9 as os
RUN \
  dnf install -y \
    bc \
    hostname \
    git \
    gcc-toolset-13-libatomic-devel \
    glibc-langpack-en \
    java-1.8.0-openjdk-headless \
    jq \
    sudo && \
  dnf install -y \
    epel-release && \
  dnf clean packages
RUN mkdir -p /ceph /.ccache

FROM os as deps
WORKDIR /ceph
RUN \
  ./install-deps.sh && \
  dnf clean all && \
  rm -rf /var/cache/dnf/*

FROM deps as sccache
ARG SCCACHE_VERSION=v0.8.0
WORKDIR /tmp
RUN \
  curl -L -o sccache.tar.gz https://github.com/mozilla/sccache/releases/download/$SCCACHE_VERSION/sccache-$SCCACHE_VERSION-$(uname -m)-unknown-linux-musl.tar.gz && \
  tar -xzf sccache.tar.gz && \
  mv sccache-*/sccache /usr/bin/ && \
  chown root:root /usr/bin/sccache && \
  restorecon -v /usr/bin/sccache && \
  rm -rf sccache*

FROM sccache as cmake
WORKDIR /ceph
ENV CMAKE_ARGS="-DCMAKE_BUILD_TYPE=RelWithDebInfo"
ENV SCCACHE_CONF=/etc/sccache.conf
RUN \
  [ -d /ceph/build ] || ./do_cmake.sh $CMAKE_ARGS
CMD [ -d /ceph/build ] || ./do_cmake.sh $CMAKE_ARGS && cd /ceph/build && ninja && sccache -s

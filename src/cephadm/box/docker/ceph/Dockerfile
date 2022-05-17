FROM quay.ceph.io/ceph-ci/ceph:master
EXPOSE 8443
COPY ../../../../ceph-volume /ceph-volume
RUN \
  cd /ceph-volume && \
  rm -rf dist && \
  python3 setup.py sdist && \
  pip3 install -U ./dist/ceph-volume-*.tar.gz

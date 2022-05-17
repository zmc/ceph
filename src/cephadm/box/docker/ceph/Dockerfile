FROM quay.ceph.io/ceph-ci/ceph:master
EXPOSE 8443
ENV CEPH_VOLUME_USE_LOOP_DEVICES=1
COPY ceph-volume /ceph-volume
RUN \
  cd /ceph-volume && \
  rm -rf dist && \
  python3 setup.py sdist && \
  pip3 install -U ./dist/ceph-volume-*.tar.gz

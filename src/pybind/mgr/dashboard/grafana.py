# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import os
import requests
import time

from . import logger
from .settings import Settings


class GrafanaError(Exception):
    pass


class GrafanaRestClient(object):

    def url_validation(self, method, path):
        response = requests.request(
            method,
            path)

        return response.status_code

    def push_dashboard(self, dashboard_obj):
        if not Settings.GRAFANA_API_URL:
            raise GrafanaError("The Grafana API URL is not set!")
        if not Settings.GRAFANA_API_URL.startswith('http'):
            raise GrafanaError("The Grafana API URL is invalid")
        if not Settings.GRAFANA_API_USERNAME:
            raise GrafanaError("The Grafana API username is not set!")
        if not Settings.GRAFANA_API_PASSWORD:
            raise GrafanaError("The Grafana API password is not set!")
        url = Settings.GRAFANA_API_URL.rstrip('/') + \
            '/api/dashboards/db'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        payload = {
            'dashboard': dashboard_obj,
            'overwrite': True,
        }
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload),
            auth=(Settings.GRAFANA_API_USERNAME,
                  Settings.GRAFANA_API_PASSWORD),
        )
        response.raise_for_status()
        return response.status_code, response.json()


class Retrier(object):
    def __init__(self, tries, sleep, func, *args, **kwargs):
        assert tries >= 1
        self.tries = int(tries)
        self.tried = 0
        self.sleep = sleep
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        result = None
        while self.tried < self.tries:
            try:
                result = self.func(*self.args, **self.kwargs)
            except Exception:
                if self.tried == self.tries - 1:
                    raise
                else:
                    self.tried += 1
                    time.sleep(self.sleep)
            else:
                return result


def load_local_dashboards():
    if os.environ.get('CEPH_DEV') == '1':
        path = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            '../../../../monitoring/grafana/dashboards/'
        ))
    else:
        path = '/etc/grafana/dashboards/ceph-dashboard'
    dashboards = dict()
    for item in filter(lambda s: s.endswith('.json'), os.listdir(path)):
        db_path = os.path.join(path, item)
        dashboards[item] = json.loads(open(db_path).read())
    return dashboards


def push_local_dashboards(tries=1, sleep=0):
    try:
        dashboards = load_local_dashboards()
    except Exception:
        logger.exception("Failed to load local dashboard files")
        raise

    def push():
        try:
            grafana = GrafanaRestClient()
            for name, body in dashboards.items():
                grafana.push_dashboard(body)
        except Exception:
            logger.exception("Failed to push dashboards to Grafana")
            raise
    retry = Retrier(tries, sleep, push)
    retry()
    return True

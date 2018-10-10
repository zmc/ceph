# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import re


from . import ApiController, BaseController, RESTController
from .. import mgr


@ApiController('/public', secure=False)
class Public(BaseController):
    @RESTController.Resource('GET')
    def version(self):
        raw_version = mgr.version
        parsed_version = re.match(
            'ceph version ([^\s]+) \(([0-9a-f]+)\) ([^\s]*)',
            raw_version,
        ).groups()
        return dict(
            number=parsed_version[0],
            hash=parsed_version[1],
            name=parsed_version[2],
        )

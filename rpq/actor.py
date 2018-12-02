# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
from rq import Connection, Queue, Worker

import logging

import redis

redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)

logger=logging.getLogger('rpq.actor')
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


HTTP_STATUS_QUEUED = 201
HTTP_STATUS_READY = 200

REQUEST_TYPE_TEST = "test"

def get_version():
    return "test-version"

def act_on_test(args):
    return {"comment":"test"}

def act(args):
    logger.debug('pass %s',args)

    if args.get('request_type','test'):
        r = act_on_test(args)

    r['request_args']=args
    r['actor']=dict(
                 version = get_version()
               )

    logger.debug("storing to redis: key %s", args)
    logger.debug("storing to redis: value %s", r)

    redis_db.set(args,
                 json.dumps(r))

    return r

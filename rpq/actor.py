# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json

from flask import url_for
from rq import Connection, Queue, Worker

import logging

import requests
import redis

import rpq.binding

redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)

logger=logging.getLogger('rpq.actor')
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)


HTTP_STATUS_READY = 200
HTTP_STATUS_QUEUED = 201
HTTP_STATUS_EQUIVALENT_TO = 210

REQUEST_TYPE_TEST = "test"
REQUEST_TYPE_WORK = "work"

def get_version():
    return "test-version"

def act_test(args):
    return {"comment":"test"}

def act_work(args):
    logger.debug('ACT to work',args)

    url = args.pop('url') # or hub?

    r = requests.get(url,params = args)

    try:
        r_json = r.json()
        status = 200
        logger.debug('work produced json:',r_json)
    except Exception as e:
        r_json = dict(exception=repr(e),content=r.content)
        status = 500

    result=dict(
                result = r_json,
                status = status,
            )


    return result

def act(pra):
    pra_hash = rpq.binding.pra_to_hash(pra)

    logger.debug('pass %s',pra)
    
    request_type = pra.get('request_type',REQUEST_TYPE_TEST)
    if  request_type == REQUEST_TYPE_TEST:
        r = act_test(pra)
    elif request_type == REQUEST_TYPE_WORK:
        r = act_work(pra)

    r['request_args']=pra
    r['actor']=dict(
                 version = get_version()
               )

    logger.debug("storing to redis: key hashe %s", pra_hash)
    logger.debug("storing to redis: key %s", pra)
    logger.debug("storing to redis: value %s", r)

    redis_db.set(pra_hash,
                 json.dumps(r))

    return r

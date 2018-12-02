# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import json
import copy

from flask import url_for
from rq import Connection, Queue, Worker

import logging

import requests
import redis

import rpq.binding
import rpq.rq

redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)

logger=logging.getLogger('rpq.actor')
logging.basicConfig(level=logging.DEBUG)


HTTP_STATUS_READY = 200
HTTP_STATUS_QUEUED = 201
HTTP_STATUS_EQUIVALENT_TO = 210

REQUEST_TYPE_TEST = "test"
REQUEST_TYPE_WORK = "work"

def get_version():
    return "test-version"

def act_test(args):
    return {"comment":"test"}, HTTP_STATUS_READY

def act_work(pra):
    logger.debug('ACT to work',pra)

    pra_copy = copy.deepcopy(pra)

    url = pra_copy.pop('url')
    args = pra_copy

    logger.debug('URL %s',url)

    r = requests.get(url,params = args)

    try:
        r_json = r.json()
        status = r.status_code
        logger.debug('work produced json: %s',r_json)
    except Exception as e:
        r_json = dict(exception=repr(e),content=r.content)
        status = 500
        logger.debug('work produced exception: %s',r_json,e)

    return r_json, status

def act(pra, callback):
    pra_hash = rpq.binding.pra_to_hash(pra)

    logger.debug('passing to actor %s',pra)
    
    request_type = pra.get('request_type',REQUEST_TYPE_WORK)
    if  request_type == REQUEST_TYPE_TEST:
        r, status = act_test(pra)
    elif request_type == REQUEST_TYPE_WORK:
        r, status = act_work(pra)

    if status == HTTP_STATUS_READY:
        meta = dict(
                request_args=pra,
                actor=dict(
                     version = get_version()
                   )
                )

        logger.debug("storing to redis: key hashe %s", pra_hash)
        logger.debug("storing to redis: key %s", pra)
        logger.debug("storing to redis: value %s", r)

        redis_db.set(pra_hash,
                     json.dumps(r))
        redis_db.set(('meta',pra_hash),
                     json.dumps(meta))

    elif status == HTTP_STATUS_EQUIVALENT_TO:
        # note equivalency

        # register new job
        logger.debug("%s equivalent to %s", pra, r['equivalent_to'])
        
        eq_r,eq_status = rpq.rq.get(r['equivalent_to'],
                          callback = pra
                        )

        logger.debug("equivalenet result %s : %s", eq_status, eq_r)

        if eq_status == HTTP_STATUS_READY:
            logger.debug("equivalenet result is COMPLETE, returing it")

            meta=dict(
                alias = r,
                eq_status = eq_status,
            )

            logger.debug("aliased storing to redis: key hashe %s", pra_hash)
            logger.debug("aliased storing to redis: key %s", pra)
            logger.debug("aliased storing to redis: value %s", eq_r)

            redis_db.set(pra_hash,
                         json.dumps(eq_r))
            redis_db.set(('meta',pra_hash),
                         json.dumps(meta))

    if callback is not None:
        logger.debug("callback to %s", callback)
        callback_r = rpq.rq.get(callback)
        logger.debug("callback result %s", callback_r)

    return r

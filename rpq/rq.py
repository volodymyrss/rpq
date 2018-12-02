import rpq.binding
import rpq.rq
import redis

from rq import Connection, Queue, Worker
from rq.job import Job
import rq

import json

import logging

logger=logging.getLogger('rpq.rq')

    
def get_redis():
    return redis.StrictRedis(host="localhost", port=6379, db=0)

def get(pra, callback = None):
    pra_hash = rpq.binding.pra_to_hash(pra)
    logger.debug("parsed request hash: %s",pra_hash)

    r = get_redis().get(pra_hash)

    if r:
        logger.debug("request DONE %s", r)
        r_json = json.loads(r)
        logger.debug("request decoded %s", r_json)
        response = r_json
        status = 200
    else:
        logger.debug("request result unavailable %s; will be searching for job", r)

        with Connection():
            j = request_to_job(pra, callback = callback)

        response = dict(job=repr(j))
        status = 201

    return response, status

def request_to_job(pra, callback = None):
    pra_hash = rpq.binding.pra_to_hash(pra)
    job_id = get_redis().get(('jobid-for-request',pra_hash))

    j = None

    q = Queue()
    if job_id:
        logger.debug("found job id %s", job_id)
        
        try:
            j = Job.fetch(job_id.decode("utf-8"))
            logger.debug("found job %s", j)
            if j.status == "finished":
                logger.debug("job %s produced no result, ignoring", j)
                j = None

        except rq.exceptions.NoSuchJobError as e:
            logger.debug("NOT found job, key stale key reference")
            get_redis().delete(('jobid-for-request',pra_hash))
            j = None

    if j is None:
        logger.debug("associated job unavailable: %s; will schedule", pra)
        j = q.enqueue(rpq.actor.act,pra,callback)
        get_redis().set(('jobid-for-request',pra_hash),j._id)
        logger.debug("scheduled job: %s",dir(j))

    return j

        #if j.status == "finished":
        #    raise RuntimeError("job is finished but no result registered")


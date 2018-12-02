from flask import Flask, request, jsonify, url_for

import logging
import requests
from collections import OrderedDict

from rq import Connection, Queue, Worker
from rq.job import Job

import redis

import rpq.actor
import rpq.binding
import rpq.routing

import json


logger = logging.getLogger('rpq.service')

logging.basicConfig(level=logging.DEBUG);

def create_app():
    app = Flask(__name__)
 #   app.config['SERVER_NAME'] = "localhost:5000"
    return app

app = create_app()

#class DependencyDelegated(Exception):
#    pass

#@app.errorhandler(DependencyDelegated)
#def handle_delegated_dependency(exception):
#    r = jsonify({})
#    r.return_code = 200
#    return r


@app.route("/async/1.0/get",methods=["GET"])
def async_get():
    logger.debug("request: %s",request.args)

    pra = rpq.binding.parse_flask_request_args()
    if 'url' not in pra:
        pra['url'] = url_for('get',_external=True)
    
    pra_hash = rpq.binding.pra_to_hash(pra)

    logger.debug("parsed request: %s",pra)
    logger.debug("parsed request hash: %s",pra_hash)

    redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)


    r = redis_db.get(pra_hash)

    if r:
        logger.debug("request DONE %s", r)
        r_json = json.loads(r)
        logger.debug("request decoded %s", r_json)
        response = jsonify(r_json)
        status = 200
    else:
        logger.debug("request result unavailable, searching for job: %s", r)

        job_id = redis_db.get(('jobid-for-request',pra_hash))

        with Connection():
            q = Queue()
            if job_id:
                logger.debug("found job id %s", job_id)
                j = Job.fetch(job_id.decode("utf-8"))
                logger.debug("found job %s", j)
            else:
                logger.debug("associated job unavailable, scheduling: %s", r)
                j = q.enqueue(rpq.actor.act,pra)
                redis_db.set(('jobid-for-request',pra_hash),j._id)
                logger.debug("scheduled job: %s",dir(j))

                if j.status == "finished":
                    raise RuntimeError("job is finished but no result registered")

            response = jsonify(dir(j))
            status = 201

    return response, status

@app.route("/1.0/get",methods=["GET"])
def get():
    pra = rpq.binding.parse_flask_request_args()
    logger.debug("request: %s",pra)

    # try cache
    
    cache = None
    if cache:
        return jsonify({}), 

    # otherwise go to routing rules

    route, args = rpq.routing.route(pra)
    
    return jsonify(
                equivalent_to = dict(url = route, args = args),
            ), rpq.actor.HTTP_STATUS_EQUIVALENT_TO


@app.route("/1.0/retrive_cache",methods=["GET"])
def retrive_cache():
    logger.debug("request to cache: %s",request.args)

    r = jsonify({})
    r.return_code = 200
    return r

@app.route("/loopback/<service>",methods=["GET"])
def loopback_service(service):
    logger.debug("request to loopback",request.args)

    r = jsonify({'echo':service})
    return r, 200

@app.route("/",methods=["GET"])
def version():
    r = jsonify({'version':'1.0'})
    return r, 200
    
logging.getLogger("rpq").setLevel(level=logging.DEBUG)
logging.getLogger("flask").setLevel(level=logging.DEBUG)

if __name__ == "__main__":
    app.run()

from flask import Flask, request, jsonify

import logging
import requests
from collections import OrderedDict
from rq import Connection, Queue, Worker
import redis

import rpq.actor
import rpq.binding

import json

cache_service = "http://cdcixn:"


logger = logging.getLogger('rpq.service')

logging.basicConfig(level=logging.DEBUG);

def create_app():
    app = Flask(__name__)
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

    pra = rpq.binding.parse_request_args()

    logger.debug("parsed request: %s",pra)

    redis_db = redis.StrictRedis(host="localhost", port=6379, db=0)

    r = redis_db.get(pra)

    if r:
        logger.debug("request DONE %s", r)
        r_json = json.loads(r)
        logger.debug("request decoded %s", r_json)
        response = jsonify(r_json)
        status = 200
    else:
        logger.debug("request unavailable, scheduling: %s", r)

        with Connection():
            q = Queue()
            j = q.enqueue(rpq.actor.act,pra)
            logger.debug("job: %s",dir(j))
            r = j.result

        response = jsonify(dir(j))
        status = 201

    return response, status

@app.route("/1.0/get",methods=["GET"])
def get():
    logger.debug("request: %s",request.args)

 #   requests.get()

    r = jsonify({})
    r.return_code = 200
    return r
    
logging.getLogger("rpq").setLevel(level=logging.DEBUG)
logging.getLogger("flask").setLevel(level=logging.DEBUG)

if __name__ == "__main__":
    app.run()

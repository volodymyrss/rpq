from flask import Flask, request, jsonify

import logging
import requests
from collections import OrderedDict
from rq import Connection, Queue, Worker
import rpq.actor

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

def parse_request_args():
    r={}
    for k in request.args:
        r[k] = request.args.get(k,'')

    return OrderedDict(r)


@app.route("/async/1.0/get",methods=["GET"])
def async_get():
    logger.debug("request: %s",request.args)

    pra = parse_request_args()

    logger.debug("parsed request: %s",pra)

    r = None
    with Connection():
        q = Queue()
        j = q.enqueue(rpq.actor.act,pra)
        logger.debug("job: %s",dir(j))
        r = j.result

    if r:
        response = jsonify(r)
        status = 200
    else:
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

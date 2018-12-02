from flask import Flask, request, jsonify, url_for

import logging
import requests
from collections import OrderedDict


import redis

import rpq.rq
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
    
    logger.debug("parsed request: %s",pra)

    result, status = rpq.rq.get(pra)

    response = jsonify(result)

    return response, status

@app.route("/1.0/get",methods=["GET"])
def get():
    pra = rpq.binding.parse_flask_request_args()

    logger.debug("request: %s",pra)

    current_routing_table_version = rpq.routing.get_routing_table_version()
    logger.debug("current routing table: %s",current_routing_table_version)

    routing_table_version = pra.get('routing_table_version',None)
    
    logger.debug("requested routing table: %s",current_routing_table_version)
    if routing_table_version is None:
        routing_table_version = current_routing_table_version
    elif current_routing_table_version != routing_table_version:
        return jsonify({'exception':'no such routing table {}, have {}'.format(routing_table_version,current_routing_table_version)}),500
    
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
    logger.debug("request to loopback %s",request.args)

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

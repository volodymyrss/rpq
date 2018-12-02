from flask import request
from collections import OrderedDict
import json
import hashlib

def parse_flask_request_args():
    r={}
    for k in request.args:
        r[k] = request.args.get(k,'')

    return OrderedDict(r)


def pra_to_hash(pra):
    return hashlib.sha224(json.dumps(pra).encode('utf-8')).hexdigest()[:16]

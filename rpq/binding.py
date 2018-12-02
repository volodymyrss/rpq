from flask import request, url_for
from collections import OrderedDict
import json
import hashlib

def parse_flask_request_args():
    r={}
    for k in request.args:
        r[k] = request.args.get(k,'')

    r['url'] = url_for('get',_external=True)

    return OrderedDict(r)


def pra_to_hash(pra):
    return hashlib.sha224(json.dumps(pra).encode('utf-8')).hexdigest()[:16]

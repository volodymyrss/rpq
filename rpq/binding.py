from flask import request
from collections import OrderedDict

def parse_request_args():
    r={}
    for k in request.args:
        r[k] = request.args.get(k,'')

    return OrderedDict(r)


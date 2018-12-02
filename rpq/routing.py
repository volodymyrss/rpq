from flask import url_for
import os
import logging
import hashlib
import copy

logger = logging.getLogger('rpq.routing')

def get_routing_table_version():
    return hashlib.sha224(os.environ.get('ODAHUB_RP_PATTERN','built-in').encode('utf-8')).hexdigest()[:16]
    

def route(pra):
    if 'service' not in pra:
        logger.warning('request is not assigned to service %s, setting to unassigned',pra)
        pra['service'] = 'unassigned'

    pra_copy = copy.deepcopy(pra)
    service = pra_copy.pop('service')

    if 'path' in pra_copy:
        path = pra_copy.pop('path')
    else:
        path = ""

    odahub_rp = os.environ.get('ODAHUB_RP_PATTERN',url_for('loopback_service',service='SERVICE',_external=True).replace('SERVICE','{service}'))

    pra_copy['url'] = odahub_rp.format(service = service, path=path)
    
    return pra_copy

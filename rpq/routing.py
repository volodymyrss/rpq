from flask import url_for
import os
import logging

logger = logging.getLogger('rpq.routing')

def route(pra):
    if 'service' not in pra:
        logger.warning('request is not assigned to service %s, setting to unassigned',pra)
        pra['service'] = 'unassigned'

    service = pra.pop('service')

    odahub_rp = os.environ.get('ODAHUB_RP_PATTERN',url_for('loopback_service',service='{service}',_external=True))
    
    return odahub_rp.format(service = service), pra

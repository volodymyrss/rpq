# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

logger=logging.getLogger('rpq.actor')

from rq import Connection, Queue, Worker

def act(args):
    logger.debug('pass %s',args)

    return dict(result_from=args)

    #with Connection():
    #    q = Queue()
    #    q.enqueue(act)

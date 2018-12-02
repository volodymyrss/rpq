# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from rq import Connection, Queue, Worker

import rpq.actor

def main():
    logger.error('starting worker')
    with Connection():
        logger.debug('starting worker')
        q = Queue()
        print("queue:",q)
        print("worker:",Worker(q).work())
        print("test")

if __name__ == '__main__':
    #with Connection():
    #    q = Queue()
    #    r = q.enqueue(rpq.actor.act)
    #    logger.info("result %s",r)

    main()

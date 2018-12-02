import pytest
from flask import url_for
import os
import logging
import time

import rpq.service

from xprocess import ProcessStarter

@pytest.fixture
def app():
    app = rpq.service.app
    print("creating app")
    return app

@pytest.fixture
def worker(xprocess):
    class Starter(ProcessStarter):
        pattern = "Cleaning registries for queue: default"
        #args = ['rqworker']
        #args = ['python','-m', 'rpq.worker']

    logfile = xprocess.ensure("myserver", Starter)
    #conn = # create a connection or url/port info to the server
    return


def test_worker(client): 
    logging.getLogger().setLevel(logging.DEBUG)

    print(client.get(url_for('get')))

def test_async_worker():
    from rq import Connection, Queue, Worker
    with Connection():
        q = Queue()
        j = q.enqueue(rpq.actor.act,dict(b=1))

    
        print("status",j.status)
        assert j.status == "queued"    

        os.system("rqworker -b --logging_level DEBUG -v")
        print("status",j.status)
        assert j.status == "finished"    

        assert j.status
        assert j.return_value

def test_async_get(client):
    logging.getLogger().setLevel(logging.DEBUG)

    r=client.get(url_for('async_get',a=time.time()))
    print("r",r)
    print("json",r.json)

    os.system("rqworker -b")

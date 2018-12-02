import pytest
from flask import url_for
import os
import logging
import time

import rpq.service



@pytest.fixture
def app():
    app = rpq.service.app
    print("creating app")
    return app

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

    request_args = dict(
                         request_timestamp = time.time(),
                         request_type = rpq.actor.REQUEST_TYPE_TEST,
                         test_payload = "test payload",
                    )

    r=client.get(url_for('async_get',**request_args))
    print("r",r)
    print("json",r.json)

    assert r.status_code == rpq.actor.HTTP_STATUS_QUEUED
    
    r=client.get(url_for('async_get',**request_args))
    assert r.status_code == rpq.actor.HTTP_STATUS_QUEUED

    os.system("rqworker -b --logging_level DEBUG -v")
    
    r=client.get(url_for('async_get',
                        **request_args
                    ))

    assert r.status_code == rpq.actor.HTTP_STATUS_READY

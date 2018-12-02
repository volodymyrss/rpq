import pytest
import requests
from flask import url_for
import os
import logging
import time

import rpq.service

from redis import Redis
from rq import Queue

def get_rq():
    return Queue(connection=Redis())

def clean_rq():
    q = get_rq()
    print("will clean",q.count)
    q.empty()

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
        j = q.enqueue(rpq.actor.act,dict(b=1,url="http://google.com/"),None)

    
        print("status",j.status)
        assert j.status == "queued"    

        os.system("rqworker -b --logging_level DEBUG -v")
        print("status",j.status)
        assert j.status == "finished"    

        assert j.status
        assert j.return_value

def test_async_get_test(live_server):
    logging.getLogger().setLevel(logging.DEBUG)

    request_args = dict(
                         request_timestamp = time.time(),
                         request_type = rpq.actor.REQUEST_TYPE_TEST,
                         test_payload = "test payload",
                    )

    r=requests.get(url_for('async_get',_external=True,**request_args))
    print("r",r)
    print("json",r.json)

    assert r.status_code == rpq.actor.HTTP_STATUS_QUEUED
    
    r=requests.get(url_for('async_get',_external=True,**request_args))
    assert r.status_code == rpq.actor.HTTP_STATUS_QUEUED

    os.system("rqworker -b --logging_level DEBUG -v")
    
    r=requests.get(url_for('async_get',
                        _external=True,
                        **request_args
                    ))

    assert r.status_code == rpq.actor.HTTP_STATUS_READY

    r_json = r.json()
    print(r_json)

def test_get(live_server):
    logging.getLogger().setLevel(logging.DEBUG)

 #   live_server.start()

    request_args = dict(
                         request_timestamp = time.time(),
                         request_type = rpq.actor.REQUEST_TYPE_TEST,
                         test_payload = "test payload",
                    )

    url = url_for('get',_external=True,**request_args)
    print("url:",url)
    r=requests.get(url)
    print("r",r)
    print("json",r.json())

    assert r.status_code == rpq.actor.HTTP_STATUS_EQUIVALENT_TO

def test_async_get(live_server):
    logging.getLogger().setLevel(logging.DEBUG)

    clean_rq()
    assert get_rq().count == 0

    request_args = dict(
                         request_timestamp = time.time(),
                         request_type = rpq.actor.REQUEST_TYPE_WORK,
                         service = "testecho",
                         test_payload = "test payload",
                    )
    
    r=requests.get(url_for('async_get',_external=True,**request_args))
    print("r",r)
    print("json",r.json)
    
    assert r.status_code == rpq.actor.HTTP_STATUS_QUEUED
    assert get_rq().count == 1
    
    r=requests.get(url_for('async_get',_external=True,**request_args))
    assert r.status_code == rpq.actor.HTTP_STATUS_QUEUED
    assert get_rq().count == 1


    os.system("rqworker -b --logging_level DEBUG -v")
    assert get_rq().count == 0

    r=requests.get(url_for('async_get',
                        _external=True,
                        **request_args
                    ))
    
    assert r.status_code == rpq.actor.HTTP_STATUS_READY

    r_json = r.json()
    print(r_json)

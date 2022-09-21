# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/9/7 9:46
import pytest
from flask import request

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)


@app.get("/t")
@app.get("/tt")
def get_t():
    return request.url


@app.post("/t")
@app.post("/tt")
def post_t():
    return request.url


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_get_t(client):
    r = client.get("/t")
    assert r.text == "http://localhost/t"
    r = client.get("/tt")
    assert r.text == "http://localhost/tt"


def test_post_t(client):
    r = client.post("/t")
    assert r.text == "http://localhost/t"
    r = client.post("/tt")
    assert r.text == "http://localhost/tt"

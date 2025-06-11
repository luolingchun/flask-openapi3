# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/9/7 9:46
import logging

from flask import request
import pytest

from flask_openapi3 import OpenAPI
from flask_openapi3.request import validate_request


logger = logging.getLogger(__name__)

app = OpenAPI(__name__)


@app.get("/t")
@app.get("/tt")
@validate_request()
def get_t():
    return request.url


@app.post("/t")
@app.post("/tt")
@validate_request()
def post_t():
    return request.url


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_get_t(client):
    response = client.get("/t")
    assert response.text == "http://localhost/t"
    response = client.get("/tt")
    assert response.text == "http://localhost/tt"


def test_post_t(client):
    response = client.post("/t")
    assert response.text == "http://localhost/t"
    response = client.post("/tt")
    assert response.text == "http://localhost/tt"

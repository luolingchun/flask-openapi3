# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/5/5 13:28

import pytest

from flask_openapi3 import Info
from flask_openapi3 import OpenAPI, APIBlueprint

info = Info(title='book API', version='1.0.0')

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True

api1 = APIBlueprint('book1', __name__, url_prefix='/api/v1/book1')
api2 = APIBlueprint('book2', __name__, url_prefix='/api/v1/book2')


@pytest.fixture
def client():
    client = app.test_client()

    return client


@api1.get('/')
def get_book():
    return 'with slash'


@api2.get('')
def get_book2():
    return 'without slash'


app.register_api(api1)
app.register_api(api2)


def test_with_slash1(client):
    resp = client.get("/api/v1/book1/")
    assert resp.status_code == 200


def test_with_slash2(client):
    resp = client.get("/api/v1/book1")
    assert resp.status_code == 308


def test_without_slash1(client):
    resp = client.get("/api/v1/book2/")
    assert resp.status_code == 404


def test_without_slash2(client):
    resp = client.get("/api/v1/book2")
    assert resp.status_code == 200


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json = resp.json
    assert _json['paths'].get('/api/v1/book1/') is not None
    assert _json['paths'].get('/api/v1/book2') is not None

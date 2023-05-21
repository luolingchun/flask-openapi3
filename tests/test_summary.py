# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/1/1 16:54

import pytest

from flask_openapi3 import Info
from flask_openapi3 import OpenAPI

info = Info(title='book API', version='1.0.0')

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get('/book', summary='new summary', description='new description')
def get_book():
    """Get a book
    to get some book by id, like:
    http://localhost:5000/book/3
    """
    return {"code": 0, "message": "ok"}


@app.get('/book2', description='new description')
def get_book2():
    """Get a book
    to get some book by id, like:
    http://localhost:5000/book/3
    """
    return {"code": 0, "message": "ok"}


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json = resp.json
    assert resp.status_code == 200
    assert _json['paths']['/book']['get']['summary'] == 'new summary'
    assert _json['paths']['/book']['get']['description'] == 'new description'
    assert _json['paths']['/book2']['get']['summary'] == 'Get a book'
    assert _json['paths']['/book2']['get']['description'] == 'new description'

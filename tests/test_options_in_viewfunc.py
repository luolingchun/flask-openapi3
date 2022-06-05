# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/5/15 14:19

import pytest

from flask_openapi3 import APIBlueprint, OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True

api = APIBlueprint(
    '/book',
    __name__,
    url_prefix='/api',
)


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get('/book', endpoint='endpoint_get_book')
def get_book():
    return 'app_book'


@api.post('/book', endpoint='endpoint_post_book')
def create_book():
    return 'api_book'


# register api
app.register_api(api)


def test_get(client):
    resp = client.get("/book")

    assert resp.text == 'app_book'
    assert 'endpoint_get_book' in app.view_functions.keys()


def test_post(client):
    resp = client.post("/api/book")

    assert resp.text == 'api_book'
    assert '/book.endpoint_post_book' in app.view_functions.keys()

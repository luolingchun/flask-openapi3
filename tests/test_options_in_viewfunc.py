# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/5/15 14:19

import pytest

from flask_openapi3 import APIBlueprint, OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


def get_operation_id_for_path_callback(*, name: str, path: str, method: str) -> str:
    print(name, path, method)
    return name


api = APIBlueprint(
    '/book',
    __name__,
    url_prefix='/api',
    operation_id_callback=get_operation_id_for_path_callback,
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


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc
    assert resp.json["paths"]["/book"]["get"]["operationId"] == "get_book_book_get"  # Default operation_id generator
    assert resp.json["paths"]["/api/book"]["post"]["operationId"] == "/book"  # Custom callback operation_id


def test_get(client):
    resp = client.get("/book")

    assert resp.text == 'app_book'
    assert 'endpoint_get_book' in app.view_functions.keys()


def test_post(client):
    resp = client.post("/api/book")

    assert resp.text == 'api_book'
    assert '/book.endpoint_post_book' in app.view_functions.keys()

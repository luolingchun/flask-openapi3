# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/2 9:09

import pytest

from flask_openapi3 import APIBlueprint, OpenAPI

app = OpenAPI(__name__)

api = APIBlueprint('book', __name__, url_prefix='/api/book')
api_english = APIBlueprint('english', __name__)
api_chinese = APIBlueprint('chinese', __name__)


@api_english.post('/english')
def create_english_book():
    return {"message": "english"}


@api_chinese.post('/chinese')
def create_chinese_book():
    return {"message": "chinese"}


# register nested api
api.register_api(api_english)
api.register_api(api_chinese)
# register api
app.register_api(api)


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc


def test_post_english(client):
    resp = client.post("/api/book/english")
    assert resp.status_code == 200


def test_post_chinese(client):
    resp = client.post("/api/book/chinese")
    assert resp.status_code == 200

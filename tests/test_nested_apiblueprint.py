# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/2 9:09

import pytest
from pydantic import BaseModel

from flask_openapi3 import APIBlueprint, OpenAPI, Tag

app = OpenAPI(__name__)

api = APIBlueprint('book', __name__, url_prefix='/api/book/<name>')
api_english = APIBlueprint('english', __name__)
api_chinese = APIBlueprint('chinese', __name__)


class BookPath(BaseModel):
    name: str


@api_english.post('/english')
def create_english_book(path: BookPath):
    return {"message": "english", "name": path.name}


@api_chinese.post('/chinese', tags=[Tag(name="chinese")])
def create_chinese_book(path: BookPath):
    return {"message": "chinese", "name": path.name}


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
    resp = client.post("/api/book/name1/english")
    assert resp.status_code == 200
    assert resp.json == {"message": "english", "name": "name1"}


def test_post_chinese(client):
    resp = client.post("/api/book/name2/chinese")
    assert resp.status_code == 200
    assert resp.json == {"message": "chinese", "name": "name2"}

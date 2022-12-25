# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/12/19 10:34

import pytest

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI, APIBlueprint

info = Info(title="book API", version="1.0.0")

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()
    return client


api1 = APIBlueprint("book1", __name__)


@api1.get('/book', tags=[Tag(name="book")])
def get_book():
    return {"code": 0, "message": "ok"}


api2 = APIBlueprint("book2", __name__)


@api2.get('/book2', tags=[Tag(name="book")])
def get_book2():
    return {"code": 0, "message": "ok"}


app.register_api(api1)
app.register_api(api2)


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json = resp.json
    assert resp.status_code == 200
    tags = _json["tags"]
    news_tags = []
    for tag in tags:
        if tag not in news_tags:
            news_tags.append(tag)
    assert news_tags == tags

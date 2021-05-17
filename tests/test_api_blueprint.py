# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/17 15:25
import json
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import APIBlueprint, OpenAPI
from flask_openapi3.models import Tag, Info

info = Info(title='book API', version='1.0.0')

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True

api = APIBlueprint('/book', __name__, url_prefix='/api')

tag = Tag(name='book', description="图书")


@pytest.fixture
def client():
    client = app.test_client()

    return client


class BookData(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='年龄')
    author: str = Field(None, min_length=2, max_length=4, description='作者')


class Path(BaseModel):
    bid: int = Field(..., description='图书id')


@api.post('/book', tags=[tag])
def create_book(body: BookData):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@app.put('/book/<int:bid>', tags=[tag])
def update_book(path: Path, body: BookData):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


# register api
app.register_api(api)


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert json.loads(json.dumps(resp.json)) == json.loads(json.dumps(app.api_doc))


def test_post(client):
    resp = client.post("/api/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/book/1", json={"age": 3})
    assert resp.status_code == 200

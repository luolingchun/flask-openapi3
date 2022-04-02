# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/2 9:09
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import APIBlueprint, OpenAPI
from flask_openapi3 import HTTPBearer
from flask_openapi3 import Tag, Info

info = Info(title='book API', version='1.0.0')
security_schemes = {"jwt": HTTPBearer(bearerFormat="JWT")}

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)

tag = Tag(name='book', description="Some Book")
security = [{"jwt": []}]


class Unauthorized(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Unauthorized!", description="Exception Information")


api = APIBlueprint(
    '/book',
    __name__,
    url_prefix='/api',
    abp_tags=[tag],
    abp_security=security,
    abp_responses={"401": Unauthorized},
    doc_ui=True
)


@pytest.fixture
def client():
    client = app.test_client()

    return client


class BookBody(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class Path(BaseModel):
    bid: int = Field(..., description='book id')


@api.get('/book')
def get_book():
    return {"code": 0, "message": "ok"}


@api.post('/book', extra_responses={"200": {"content": {"text/csv": {"schema": {"type": "string"}}}}})
def create_book(body: BookBody):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.put('/book/<int:bid>', operation_id='update')
def update_book(path: Path, body: BookBody):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


sub_api = APIBlueprint(
    '/sub_book',
    __name__,
    url_prefix='/sub_api',
    abp_tags=[tag],
    abp_security=security,
    abp_responses={"401": Unauthorized},
    doc_ui=True
)


@sub_api.post('/sub_book')
def create_sub_book():
    return {'code': 0, 'message': 'ok', 'data': 'post sub book'}


@sub_api.get('/sub_book')
def get_sub_book():
    return {'code': 0, 'message': 'ok', 'data': 'get sub book'}


# register sub api blueprint
api.register_api(sub_api)
# register api blueprint
app.register_api(api)


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc


def test_post(client):
    resp = client.post("/api/book", json={"age": 3})
    assert resp.status_code == 200


def test_get(client):
    resp = client.get("/api/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/api/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_sub_get(client):
    resp = client.get("/api/sub_api/sub_book", json={"age": 3})
    assert resp.status_code == 200


def test_sub_post(client):
    resp = client.post("/api/sub_api/sub_book")
    assert resp.status_code == 200

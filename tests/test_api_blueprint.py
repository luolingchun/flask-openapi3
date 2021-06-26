# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/17 15:25

from typing import Optional

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import APIBlueprint, OpenAPI
from flask_openapi3.models import Tag, Info
from flask_openapi3.models.security import HTTPBearer

info = Info(title='book API', version='1.0.0')
securitySchemes = {"jwt": HTTPBearer(bearerFormat="JWT")}

app = OpenAPI(__name__, info=info, securitySchemes=securitySchemes)
app.config["TESTING"] = True

tag = Tag(name='book', description="Book")
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
    abp_responses={"401": Unauthorized}
)


@pytest.fixture
def client():
    client = app.test_client()

    return client


class BookData(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class Path(BaseModel):
    bid: int = Field(..., description='book id')


@api.post('/book', doc_ui=False)
def create_book(body: BookData):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@app.put('/book/<int:bid>')
def update_book(path: Path, body: BookData):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


# register api
app.register_api(api)


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc


def test_post(client):
    resp = client.post("/api/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/book/1", json={"age": 3})
    assert resp.status_code == 200

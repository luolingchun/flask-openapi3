# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/6 16:38
from __future__ import annotations

from http import HTTPStatus
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI

info = Info(title='book API', version='1.0.0')

jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}
security_schemes = {"jwt": jwt}


class NotFoundResponse(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Resource not found!", description="Exception Information")


doc_prefix = '/v1/openapi'
app = OpenAPI(
    __name__,
    info=info,
    doc_prefix=doc_prefix,
    security_schemes=security_schemes,
    responses={"404": NotFoundResponse}
)
app.config["TESTING"] = True

security = [{"jwt": []}]
book_tag = Tag(name='book', description='Book')


class BookQuery(BaseModel):
    age: Optional[int] = Field(None, description='Age')


class BookBody(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BookPath(BaseModel):
    bid: int = Field(..., description='book id')


class BookBodyWithID(BaseModel):
    bid: int = Field(..., description='book id')
    age: Optional[int] = Field(None, ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


class BaseResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")


class BookResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")
    data: BookBodyWithID

    model_config = dict(
        openapi_extra={
            "content": {
                "text/csv": {"schema": {"type": "string"}}
            }
        }
    )


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    responses={"200": BookResponse},
    security=security
)
def get_book(path: BookPath):
    """Get a book
    to get some book by id, like:
    http://localhost:5000/book/3
    """
    if path.bid == 4:
        return NotFoundResponse().model_dump(), 404
    return {"code": 0, "message": "ok", "data": {"bid": path.bid, "age": 3, "author": 'no'}}


@app.get('/book', tags=[book_tag])
def get_books(query: BookBody):
    """get books
    to get all books
    """
    assert query.age == 3
    assert query.author == 'joy'
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"bid": 1, "age": query.age, "author": "b1"},
            {"bid": 2, "age": query.age, "author": "b2"}
        ]
    }


@app.post('/book', tags=[book_tag], responses={"200": BaseResponse})
def create_book(body: BookBody):
    assert body.age == 3
    return {"code": 0, "message": "ok"}, HTTPStatus.OK


@app.put('/book/<int:bid>', tags=[book_tag])
def update_book(path: BookPath, body: BookBody):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@app.patch('/book/<int:bid>', tags=[book_tag])
def update_book1(path: BookPath, body: BookBody):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@app.delete('/book/<int:bid>', tags=[book_tag])
def delete_book(path: BookPath):
    assert path.bid == 1
    return {"code": 0, "message": "ok"}


def test_openapi(client):
    resp = client.get(f"{doc_prefix}/openapi.json")
    print(resp.json)
    assert resp.status_code == 200
    assert resp.json == app.api_doc

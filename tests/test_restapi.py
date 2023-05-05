# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/6 16:38
from __future__ import annotations

from http import HTTPStatus
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import HTTPBearer
from flask_openapi3 import Info, Tag
from flask_openapi3 import OpenAPI

info = Info(title='book API', version='1.0.0')
security_schemes = {"jwt": HTTPBearer(bearerFormat="JWT")}


class NotFoundResponse(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Resource not found!", description="Exception Information")

def get_operation_id_for_path_callback(*, name: str, path: str, method: str) -> str:
    return name


app = OpenAPI(
    __name__,
    info=info,
    security_schemes=security_schemes,
    responses={"404": NotFoundResponse},
    operation_id_callback=get_operation_id_for_path_callback,
    
)
app.config["TESTING"] = True
security = [{"jwt": []}]
book_tag = Tag(name='book', description='Book')

app.config["VALIDATE_RESPONSE"] = True


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


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get(
    '/book/<int:bid>',
    tags=[book_tag],
    responses={"200": BookResponse},
    extra_responses={"200": {"content": {"text/csv": {"schema": {"type": "string"}}}}},
    security=security
)
def get_book(path: BookPath):
    """Get book
    Get some book by id, like:
    http://localhost:5000/book/3
    """
    if path.bid == 4:
        return NotFoundResponse().dict(), 404
    return {"code": 0, "message": "ok", "data": {"bid": path.bid, "age": 3, "author": 'no'}}


@app.get('/book', tags=[book_tag])
def get_books(query: BookBody):
    """get books
    get all books
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


@app.delete('/book/<int:bid>', tags=[book_tag], operation_id="delete")
def delete_book(path: BookPath):
    assert path.bid == 1
    return {"code": 0, "message": "ok"}


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    print(resp.json)
    assert resp.status_code == 200
    assert resp.json == app.api_doc
    assert resp.json["paths"]["/book"]["get"]["operationId"] == "get_books"
    assert resp.json["paths"]["/book/{bid}"]["delete"]["operationId"] == "delete"


def test_get(client):
    resp = client.get("/book?age=3&author=joy")
    assert resp.status_code == 200


def test_get_by_id_4(client):
    resp = client.get("/book/4?age=3&author=joy")
    assert resp.status_code == 404


def test_post(client):
    resp = client.post("/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_patch(client):
    resp = client.patch("/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_delete(client):
    resp = client.delete("/book/1")
    assert resp.status_code == 200

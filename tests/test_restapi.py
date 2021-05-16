# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/6 16:38
import json
from typing import Optional

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI
from flask_openapi3.models import Info, Tag
from flask_openapi3.models.security import HTTPBearer

info = Info(title='book API', version='1.0.0')
securitySchemes = {"jwt": HTTPBearer(bearerFormat="JWT")}

app = OpenAPI(__name__, info=info, securitySchemes=securitySchemes)
app.config["TESTING"] = True

book_tag = Tag(name='book', description='图书')


class Path(BaseModel):
    bid: int = Field(..., description='图书id')


class BookData(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='年龄')
    author: str = Field(None, min_length=2, max_length=4, description='作者')


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get('/book', tags=[book_tag])
def get_books(query: BookData):
    """get books
    get all books
    """
    assert query.age == 3
    assert query.author == 'joy'
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"bid": 1, "age": query.age, "author": query.author},
            {"bid": 2, "age": query.age, "author": query.author}
        ]
    }


@app.post('/book', tags=[book_tag])
def create_book(body: BookData):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@app.put('/book/<int:bid>', tags=[book_tag])
def update_book(path: Path, body: BookData):
    print(path)
    print(body)
    return {"code": 0, "message": "ok"}


@app.delete('/book/<int:bid>', tags=[book_tag])
def delete_book(path: Path):
    print(path)
    return {"code": 0, "message": "ok"}


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert json.loads(json.dumps(resp.json)) == json.loads(json.dumps(app.api_doc))


def test_get(client):
    resp = client.get("/book?age=3&author=joy")
    assert resp.status_code == 200

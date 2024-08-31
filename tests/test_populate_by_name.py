# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/8/31 15:35
import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


class BookQuery(BaseModel):
    age: int
    author: str = Field(..., alias="author_name")

    model_config = {"populate_by_name": True}


@app.get("/book", summary="get books")
def get_book(query: BookQuery):
    """
    get all books
    """
    return {
        "code": 0,
        "message": "ok",
        "data": [
            {"bid": 1, "age": query.age, "author": query.author},
            {"bid": 2, "age": query.age, "author": query.author}
        ]
    }


def test_openapi(client):
    resp = client.get("/book?age=1&author=aa")
    assert resp.status_code == 200
    resp = client.get("/book?age=1&author_name=aa")
    assert resp.status_code == 200

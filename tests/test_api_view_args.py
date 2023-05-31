# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/11/4 14:41

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import APIView
from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True

api_view = APIView(url_prefix="/api/v1")


class BookPath(BaseModel):
    id: int = Field(..., description="book ID")


@api_view.route("/book")
class BookListAPIView:
    def __init__(self, view_kwargs=None):
        self.a = view_kwargs.get("a")

    @api_view.doc(summary="get book list")
    def get(self):
        return {"a": self.a}


@api_view.route("/book/<id>")
class BookAPIView:
    def __init__(self, view_kwargs=None):
        self.b = view_kwargs.get("b")

    @api_view.doc(summary="get book list")
    def get(self, path: BookPath):
        print(path)
        return {"b": self.b}


app.register_api_view(
    api_view,
    view_kwargs={
        "a": 1,
        "b": 2
    }
)


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_get_list_view_kwargs(client):
    resp = client.get("/api/v1/book")
    assert resp.status_code == 200

    assert resp.json["a"] == 1


def test_get_view_kwargs(client):
    resp = client.get("/api/v1/book/1")
    assert resp.status_code == 200

    assert resp.json["b"] == 2

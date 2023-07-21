# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/11/4 14:41

from typing import Optional

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import APIView
from flask_openapi3 import OpenAPI, Tag, Info

info = Info(title='book API', version='1.0.0')
jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}
security_schemes = {"jwt": jwt}

app = OpenAPI(__name__, info=info, security_schemes=security_schemes)
app.config["TESTING"] = True
security = [{"jwt": []}]

api_view = APIView(url_prefix="/api/v1/<name>", view_tags=[Tag(name="book")], view_security=security)


class BookPath(BaseModel):
    id: int = Field(..., description="book ID")
    name: str


class BookQuery(BaseModel):
    age: Optional[int] = Field(None, description='Age')


class BookBody(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: str = Field(None, min_length=2, max_length=4, description='Author')


@api_view.route("/book")
class BookListAPIView:
    a = 1

    @api_view.doc(summary="get book list")
    def get(self, query: BookQuery):
        print(self.a)
        return query.json()

    @api_view.doc(summary="create book")
    def post(self, body: BookBody):
        """description for a created book"""
        return body.json()


@api_view.route("/book/<id>")
class BookAPIView:
    @api_view.doc(summary="get book")
    def get(self, path: BookPath):
        print(path)
        return "get"

    @api_view.doc(summary="update book", operation_id="update")
    def put(self, path: BookPath):
        print(path)
        return "put"

    @api_view.doc(summary="delete book", deprecated=True)
    def delete(self, path: BookPath):
        print(path)
        return "delete"


app.register_api_view(api_view)


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc
    assert resp.json["paths"]["/api/v1/{name}/book/{id}"]["put"]["operationId"] == "update"
    assert resp.json["paths"]["/api/v1/{name}/book/{id}"]["delete"][
               "operationId"] == "BookAPIView_delete_book__id__delete"


def test_get_list(client):
    resp = client.get("/api/v1/name1/book")
    assert resp.status_code == 200


def test_post(client):
    resp = client.post("/api/v1/name1/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/api/v1/name1/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_get(client):
    resp = client.get("/api/v1/name1/book/1")
    assert resp.status_code == 200


def test_delete(client):
    resp = client.delete("/api/v1/name1/book/1")
    assert resp.status_code == 200

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/12/5 10:27

from typing import Optional

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI, APIView

app = OpenAPI(__name__)
app.config["TESTING"] = True
api_view = APIView(url_prefix="/api/v1")


class Query(BaseModel):
    q: str


class BookQuery(BaseModel):
    age: Optional[int] = Field(None, description="Age")


class BookBody(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description="Age")
    author: str = Field(None, min_length=2, max_length=4, description="Author")


@app.get("/open/api")
async def get_openapi(query: Query):
    print(query)
    return "GET, OpenAPI!"


@app.post("/open/api")
async def post_openapi(body: Query):
    print(body)
    return "POST, OpenAPI!"


@api_view.route("/book")
class BookListAPIView:

    @api_view.doc(summary="get book list")
    async def get(self, query: BookQuery):
        return query.model_dump_json()

    @api_view.doc(summary="create book")
    async def post(self, body: BookBody):
        """description for a created book"""
        return body.model_dump_json()


app.register_api_view(api_view)


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc


def test_get_openapi(client):
    resp = client.get("/open/api?q=1")
    assert resp.status_code == 200
    assert resp.text == "GET, OpenAPI!"


def test_post_openapi(client):
    resp = client.post("/open/api", json={"q": "string"})
    assert resp.status_code == 200
    assert resp.text == "POST, OpenAPI!"


def test_get_list(client):
    resp = client.get("/api/v1/book")
    assert resp.status_code == 200


def test_post(client):
    resp = client.post("/api/v1/book", json={"age": 1})
    assert resp.status_code == 422

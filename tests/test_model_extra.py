# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/11/20 14:45
import logging
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
import pytest

from flask_openapi3 import OpenAPI
from flask_openapi3.request import validate_request


logger = logging.getLogger(__name__)

app = OpenAPI(__name__)
app.config["TESTING"] = True


class BookQuery(BaseModel):
    age: Optional[int] = Field(None, description="Age")

    model_config = ConfigDict(extra="allow")


class BookForm(BaseModel):
    string: str

    model_config = ConfigDict(extra="forbid")


class BookHeader(BaseModel):
    api_key: str = Field(..., description="API Key")

    model_config = ConfigDict(extra="forbid")


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get("/book")
@validate_request()
def get_books(query: BookQuery):
    """get books
    to get all books
    """
    assert query.age == 3
    assert query.author == "joy"
    return {"code": 0, "message": "ok"}


@app.post("/form")
@validate_request()
def api_form(form: BookForm):
    logger.info(form)
    return {"code": 0, "message": "ok"}


@app.get("/header")
@validate_request()
def get_book(header: BookHeader):
    return header.model_dump(by_alias=True)


def test_query(client):
    resp = client.get("/book?age=3&author=joy")
    assert resp.status_code == 200


def test_form(client):
    data = {"string": "a", "string_list": ["a", "b", "c"]}
    r = client.post("/form", data=data, content_type="multipart/form-data")
    assert r.status_code == 422


def test_header(client):
    headers = {"Hello1": "111", "hello2": "222", "api_key": "333", "api_type": "A", "x-hello": "444"}
    resp = client.get("/header", headers=headers)
    assert resp.status_code == 422

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/9/29 10:36
import logging

from pydantic import BaseModel
import pytest

from flask_openapi3 import OpenAPI
from flask_openapi3.request import validate_request


logger = logging.getLogger(__name__)
app = OpenAPI(__name__)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


class BookQuery(BaseModel):
    age: list[int] = [1, 2]


class BookForm(BaseModel):
    age: list[float] = [3, 4]


@app.get("/query")
@validate_request()
def api_query(query: BookQuery):
    assert query.age == [1, 2]
    return {"code": 0, "message": "ok"}


@app.post("/form")
@validate_request()
def api_form(form: BookForm):
    assert form.age == [3, 4]
    return {"code": 0, "message": "ok"}


def test_query(client):
    client.get("/query")


def test_form(client):
    client.post("/form")

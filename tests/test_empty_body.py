# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/12/1 9:39

from functools import wraps

import pytest
from flask import jsonify, request
from pydantic import BaseModel

from flask_openapi3 import Info, OpenAPI
from flask_openapi3.request import validate

info = Info(title="book API", version="1.0.0")

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True


class CreateBookBody(BaseModel):
    pass

    model_config = {
        "extra": "allow",
    }


class BookBody(BaseModel):
    name: str


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.post("/book")
def create_book(body: CreateBookBody):
    print(body.model_dump())
    return {"code": 0, "message": "ok"}


def check_header(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.headers.get("foo") != "bar":
            return jsonify({"error": "Access Denied"}), 400
        return func(*args, **kwargs)

    return wrapper


@app.post("/book2", delegated_validation=True)
@check_header
@validate()
def create_book_validate(body: BookBody):
    print(body.model_dump())
    return {"code": 0, "message": "ok"}


@app.post("/book3")
@check_header
def create_book_validate_alt(body: BookBody):
    print(body.model_dump())
    return {"code": 0, "message": "ok"}


def test_post(client):
    resp = client.post("/book", json={"aaa": 111, "bbb": 222})
    print(resp.json)
    assert resp.status_code == 200


def test_post_auth_check(client):
    resp = client.post("/book2", json={"bla": 111}, headers={"nope": "nope"})
    print(resp.json)
    assert resp.status_code == 400
    assert resp.json == {"error": "Access Denied"}

    resp = client.post("/book2", json={"bla": 111}, headers={"foo": "bar"})
    print(resp.json)
    assert resp.status_code == 422
    assert resp.json == [
        {
            "type": "missing",
            "loc": ["name"],
            "msg": "Field required",
            "input": {"bla": 111},
            "url": "https://errors.pydantic.dev/2.11/v/missing",
        }
    ]


def test_post_auth_check_alternate(client):
    resp = client.post("/book3", json={"bla": 111}, headers={"nope": "nope"})
    assert resp.status_code == 400
    assert resp.json == {"error": "Access Denied"}

    resp = client.post("/book3", json={"bla": 111}, headers={"foo": "bar"})
    assert resp.status_code == 422
    assert resp.json == [
        {
            "type": "missing",
            "loc": ["name"],
            "msg": "Field required",
            "input": {"bla": 111},
            "url": "https://errors.pydantic.dev/2.11/v/missing",
        }
    ]

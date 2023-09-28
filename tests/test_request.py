# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/9/2 15:35
from functools import wraps
from typing import List, Optional

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI, FileStorage, RawModel

app = OpenAPI(__name__)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


class BookForm(BaseModel):
    file: FileStorage
    files: List[FileStorage]
    string: str
    string_list: List[str]


class BookQuery(BaseModel):
    age: List[int]


class BookBody(BaseModel):
    age: int


class BookCookie(BaseModel):
    token: Optional[str] = None


class BookHeader(BaseModel):
    Hello1: str = Field("what's up", max_length=12, description="sds")
    # required
    hello2: str = Field(..., max_length=12, description="sds")
    api_key: str = Field(..., description="API Key")
    x_hello: str = Field(..., max_length=12, description='Header with alias to support dash', alias="x-hello")


def decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@app.get("/query")
@decorator
def api_query(query: BookQuery):
    print(query)
    return {"code": 0, "message": "ok"}


@app.post("/form")
def api_form(form: BookForm):
    print(form)
    return {"code": 0, "message": "ok"}


@app.post("/body")
def api_error_json(body: BookBody):
    print(body)
    return {"code": 0, "message": "ok"}


@app.get("/header")
def get_book(header: BookHeader):
    return header.model_dump(by_alias=True)


@app.post("/cookie")
def api_cookie(cookie: BookCookie):
    print(cookie)
    return {"code": 0, "message": "ok"}


class BookRaw(RawModel):
    mimetypes = ["text/csv", "application/json"]


@app.post("/raw")
def api_raw(raw: BookRaw):
    # raw equals to flask.request
    assert raw.data == b"raw"
    assert raw.mimetype == "text/plain"
    return "ok"


def test_query(client):
    r = client.get("/query")
    print(r.json)
    assert r.status_code == 200


def test_form(client):
    from io import BytesIO
    data = {
        "file": (BytesIO(b"post-data"), "filename"),
        "files": [(BytesIO(b"post-data"), "filename"), (BytesIO(b"post-data"), "filename")],
        "string": "a",
        "string_list": ["a", "b", "c"]
    }
    r = client.post("/form", data=data, content_type="multipart/form-data")
    assert r.status_code == 200


def test_error_json(client):
    r = client.post("/body", json="{age: 1}")
    assert r.status_code == 422


def test_cookie(client):
    r = client.post("/cookie")
    print(r.json)
    assert r.status_code == 200


def test_header(client):
    headers = {"Hello1": "111", "hello2": "222", "api_key": "333", "x-hello": "444"}
    resp = client.get("/header", headers=headers)
    print(resp.json)
    assert resp.status_code == 200
    assert resp.json == headers


def test_raw(client):
    resp = client.post("/raw", data="raw", headers={"Content-Type": "text/plain"})
    assert resp.status_code == 200

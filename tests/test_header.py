# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/12/30 20:40


import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import Info
from flask_openapi3 import OpenAPI

info = Info(title='header API', version='1.0.0')
app = OpenAPI(__name__, info=info)


class Headers(BaseModel):
    Hello1: str = Field("what's up", max_length=12, description='sds')
    # required
    hello2: str = Field(..., max_length=12, description='sds')


app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get('/book')
def get_book(header: Headers):
    return header.dict()


def test_get(client):
    headers = {'Hello1': '111', 'hello2': '222'}
    resp = client.get("/book", headers=headers)
    print(resp.json)
    assert resp.status_code == 200
    assert resp.json == headers

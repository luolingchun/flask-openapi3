# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/12/1 9:39

import pytest
from pydantic import BaseModel, Extra

from flask_openapi3 import Info, OpenAPI

info = Info(title='book API', version='1.0.0')

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True


class CreateBookBody(BaseModel):
    pass

    class Config:
        extra = Extra.allow


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.post('/book')
def create_book(body: CreateBookBody):
    print(body.dict())
    return {"code": 0, "message": "ok"}


def test_post(client):
    resp = client.post("/book", json={'aaa': 111, 'bbb': 222})
    print(resp.json)
    assert resp.status_code == 200

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/5/22 8:05

import pytest
from pydantic import BaseModel

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


class MyModel(BaseModel):
    text: str


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.post('/path/')
def create_book1(body: MyModel):
    return body.text


def test_post(client):
    my_model = MyModel(text='1')
    resp = client.post("/path/", json=my_model.model_dump_json())
    assert resp.status_code == 200

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/4/19 20:53

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


class MyModel(BaseModel):
    num_1: int = Field(..., ge=1, le=10)
    num_2: int = Field(..., gt=1, lt=10)


@app.post('/book')
def create_book(body: MyModel):
    print(body)  # pragma: no cover


@pytest.fixture
def client():
    client = app.test_client()
    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc

    model_props = resp.json['components']['schemas']['MyModel']['properties']
    num_1_props = model_props['num_1']
    num_2_props = model_props['num_2']

    assert num_1_props['minimum'] == 1
    assert num_1_props['maximum'] == 10
    assert num_2_props['exclusiveMinimum'] == 1
    assert num_2_props['exclusiveMaximum'] == 10

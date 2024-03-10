# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/3/10 14:48
import pytest

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__, swagger_config={"validatorUrl": "https://www.b.com"})
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc


def test_swagger(client):
    resp = client.get("/openapi/swagger")
    assert resp.status_code == 200
    assert "https://www.b.com" in resp.text

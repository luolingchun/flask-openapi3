# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/6 16:38
from __future__ import annotations

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import Info
from flask_openapi3 import OpenAPI

info = Info(title='book API', version='1.0.0')

jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}
security_schemes = {"jwt": jwt}


class NotFoundResponse(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Resource not found!", description="Exception Information")


doc_prefix = '/v1/openapi'
app = OpenAPI(
    __name__,
    info=info,
    doc_prefix=doc_prefix,
    security_schemes=security_schemes,
    responses={"404": NotFoundResponse}
)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get(f"{doc_prefix}/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc

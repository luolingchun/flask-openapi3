# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/9 11:23
from http import HTTPStatus

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI, APIBlueprint

app = OpenAPI(__name__)
app.config["TESTING"] = True
api = APIBlueprint("/api", __name__, url_prefix="/api")


class BookResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")


class BookPath(BaseModel):
    bid: int = Field(..., description="book id")


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get(
    "/book/<int:bid>",
    responses={
        HTTPStatus.OK: BookResponse,
        "201": BookResponse,
        202: {"content": {"text/html": {"schema": {"type": "string"}}}},
        204: None
    }
)
def get_book(path: BookPath):
    print(path)
    return {"code": 0, "message": "ok"}


@api.get("/book", responses={HTTPStatus.OK: BookResponse, "201": BookResponse, 204: None})
def get_api_book():
    return {"code": 0, "message": "ok"}


app.register_api(api)


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json = resp.json
    assert resp.status_code == 200
    assert _json["paths"]["/book/{bid}"]["get"]["responses"].keys() - ["200", "201", "202", "204"] == {"422"}
    assert _json["paths"]["/api/book"]["get"]["responses"].keys() - ["200", "201", "202", "204"] == set()

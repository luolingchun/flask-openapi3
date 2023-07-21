# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/21 10:32

import pytest
from flask import make_response, current_app
from pydantic import BaseModel, Field, ValidationError

from flask_openapi3 import OpenAPI


class ValidationErrorModel(BaseModel):
    code: str
    message: str


def validation_error_callback(e: ValidationError):
    validation_error_object = ValidationErrorModel(code="400", message=e.json())
    response = make_response(validation_error_object.json())
    response.headers["Content-Type"] = "application/json"
    response.status_code = getattr(current_app, "validation_error_status", 422)
    return response


app = OpenAPI(
    __name__,
    validation_error_status=400,
    validation_error_model=ValidationErrorModel,
    validation_error_callback=validation_error_callback
)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()
    return client


class BookQuery(BaseModel):
    age: int = Field(None, description='Age')


@app.get("/query")
def api_query(query: BookQuery):
    print(query)
    return {"code": 0, "message": "ok"}


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json["components"]["schemas"]["ValidationErrorModel"] == ValidationErrorModel.schema()


def test_api_query(client):
    resp = client.get("/query?age=abc")
    print(resp.json)
    assert resp.status_code == 400

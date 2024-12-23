# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/17 15:25
from decimal import Decimal
from typing import Optional

import pytest
from pydantic import BaseModel, Field, computed_field

from flask_openapi3 import APIBlueprint, OpenAPI
from flask_openapi3 import Tag, Info


app = OpenAPI(__name__)
app.config["TESTING"] = True

api = APIBlueprint(
    '/book',
    __name__,
    url_prefix='/api',
    separate_input_output_schemas=True,
)

@pytest.fixture
def client():
    client = app.test_client()

    return client


class Status(BaseModel):
    code: int = Field(0, description='Status Code')
    message: str = Field('ok', description='Message')


class BookModel(BaseModel):
    age: Optional[int] = Field(..., ge=2, le=4, description='Age')
    author: Optional[str] = Field(None, min_length=2, max_length=4, description='Author')
    # price shouldn't be in the response schema
    price: Optional[Decimal] = Field(None, gt=0, description='Price', exclude=True)

    # isNew shouldn't be in the request schema
    @computed_field(alias='isNew')
    def is_new(self) -> bool:
        return self.age < 2


class BookPath(BaseModel):
    bid: int = Field(..., description='book id')


@api.post('/book', responses={"200": Status})
def create_book(body: BookModel):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.put('/book/<int:bid>', responses={"200": BookModel}, separate_input_output_schemas=False)
def update_book__same_schemas(path: BookPath, body: BookModel):
    assert path.bid == 1
    assert body.age == 3
    return body.model_dump()

@api.put('/v2/book/<int:bid>', responses={"200": BookModel})
def update_book_v2_separate_input_output_schemas(path: BookPath, body: BookModel):
    assert path.bid == 1
    assert body.age == 3
    return body.model_dump()

@api.put('/v3/book/<int:bid>', responses={"200": BookModel}, separate_input_output_schemas=True)
def update_book_v3_separate_input_output_schemas(path: BookPath, body: BookModel):
    assert path.bid == 1
    assert body.age == 3
    return body.model_dump()

# register api
app.register_api(api)

def get_response_ref(resp):
    return resp["responses"]["200"]["content"]["application/json"]["schema"]["$ref"]

def get_request_ref(req):
    return req["requestBody"]["content"]["application/json"]["schema"]["$ref"]

def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc
    components = resp.json["components"]
    paths = resp.json["paths"]
    assert set(components["schemas"].keys()) == {
        'BookModel-Input', 'Status-Output', 'ValidationErrorModel', 'BookModel-Output', 'BookModel'
    }
    assert set(components["schemas"]["BookModel"]["properties"].keys()) == {"age", "author", "price"}
    assert set(components["schemas"]["BookModel-Input"]["properties"].keys()) == {"age", "author", "price"}
    assert set(components["schemas"]["BookModel-Output"]["properties"].keys()) == {"age", "author", "isNew"}

    # create
    assert get_response_ref(paths["/api/book"]["post"]) == "#/components/schemas/Status-Output"
    assert get_request_ref(paths["/api/book"]["post"]) == "#/components/schemas/BookModel-Input"

    # update with same schemas
    assert get_response_ref(paths["/api/book/{bid}"]["put"]) == "#/components/schemas/BookModel"
    assert get_request_ref(paths["/api/book/{bid}"]["put"]) == "#/components/schemas/BookModel"

    # update with separate schemas (fall back from APIBlueprint level)
    assert get_response_ref(paths["/api/v2/book/{bid}"]["put"]) == "#/components/schemas/BookModel-Output"
    assert get_request_ref(paths["/api/v2/book/{bid}"]["put"]) == "#/components/schemas/BookModel-Input"

    # update with separate schemas (specified at API level)
    assert get_response_ref(paths["/api/v3/book/{bid}"]["put"]) == "#/components/schemas/BookModel-Output"
    assert get_request_ref(paths["/api/v3/book/{bid}"]["put"]) == "#/components/schemas/BookModel-Input"

def test_post(client):
    resp = client.post("/api/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/api/book/1", json={"age": 3})
    assert resp.status_code == 200

    resp = client.put("/api/book/1", json={"age": 3})
    assert resp.status_code == 200

    resp = client.put("/api/v2/book/1", json={"age": 3})
    assert resp.status_code == 200

    resp = client.put("/api/v3/book/1", json={"age": 3})
    assert resp.status_code == 200

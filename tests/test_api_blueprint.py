# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/17 15:25


import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import APIBlueprint, Info, OpenAPI, Tag

info = Info(title="book API", version="1.0.0")

jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
security_schemes = {"jwt": jwt}


def operation_id_callback(*, bp_name: str = None, name: str, path: str, method: str) -> str:
    assert bp_name == "/book"
    return name


app = OpenAPI(__name__, info=info, security_schemes=security_schemes)
app.config["TESTING"] = True

tag = Tag(name="book", description="Book")
security = [{"jwt": []}]


class Unauthorized(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Unauthorized!", description="Exception Information")


api = APIBlueprint(
    "/book",
    __name__,
    url_prefix="/api",
    abp_tags=[tag],
    abp_security=security,
    abp_responses={"401": Unauthorized},
    operation_id_callback=operation_id_callback,
)

try:
    api.register_api(api)
except ValueError as e:
    assert str(e) == "Cannot register a api blueprint on itself"


@pytest.fixture
def client():
    client = app.test_client()

    return client


class BookBody(BaseModel):
    age: int | None = Field(..., ge=2, le=4, description="Age")
    author: str = Field(None, min_length=2, max_length=4, description="Author")


class BookPath(BaseModel):
    bid: int = Field(..., description="book id")


@api.post("/book", doc_ui=False)
def create_book(body: BookBody):
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.put("/book/<int:bid>", operation_id="update")
def update_book(path: BookPath, body: BookBody):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.patch("/book/<int:bid>")
def update_book1(path: BookPath, body: BookBody):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.patch("/v2/book/<int:bid>")
def update_book1_v2(path: BookPath, body: BookBody):
    assert path.bid == 1
    assert body.age == 3
    return {"code": 0, "message": "ok"}


@api.delete("/book/<int:bid>")
def delete_book(path: BookPath):
    assert path.bid == 1
    return {"code": 0, "message": "ok"}


@api.get("/book/<int:bid>")
def get_book(path: BookPath):
    """Get Book
    Here is a book
    Here's another line in the description
    """
    return {"title": "test", "Author": "author"}


# register api
app.register_api(api)


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    assert resp.json == app.api_doc
    assert resp.json["paths"]["/api/book/{bid}"]["put"]["operationId"] == "update"
    assert resp.json["paths"]["/api/book/{bid}"]["delete"]["operationId"] == "delete_book"
    expected_description = "Here is a book<br/>Here's another line in the description"
    assert resp.json["paths"]["/api/book/{bid}"]["get"]["description"] == expected_description


def test_post(client):
    resp = client.post("/api/book", json={"age": 3})
    assert resp.status_code == 200


def test_put(client):
    resp = client.put("/api/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_patch(client):
    resp = client.patch("/api/book/1", json={"age": 3})
    assert resp.status_code == 200

    resp = client.patch("/api/v2/book/1", json={"age": 3})
    assert resp.status_code == 200


def test_delete(client):
    resp = client.delete("/api/book/1")
    assert resp.status_code == 200


# Create a second blueprint here to test when `url_prefix` is None
author_api = APIBlueprint(
    "/author",
    __name__,
    abp_tags=[tag],
    abp_security=security,
    abp_responses={"401": Unauthorized},
)


class AuthorBody(BaseModel):
    age: int | None = Field(..., ge=1, le=100, description="Age")


@author_api.post("/<int:aid>")
def get_author(body: AuthorBody):
    pass


def create_app():
    app = OpenAPI(__name__, info=info, security_schemes=security_schemes)
    app.register_api(api, url_prefix="/1.0")
    app.register_api(author_api, url_prefix="/1.0/author")


# Invoke twice to ensure that call is idempotent
create_app()
create_app()


def test_blueprint_path_and_prefix():
    assert list(api.paths.keys()) == ["/1.0/book/{bid}", "/1.0/v2/book/{bid}"]
    assert list(author_api.paths.keys()) == ["/1.0/author/{aid}"]

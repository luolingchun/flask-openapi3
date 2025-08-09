from functools import wraps

import pytest
from flask import request
from pydantic import BaseModel, Field

from flask_openapi3 import APIView, Info, OpenAPI, Tag
from flask_openapi3.request import validate_request


class BookNamePath(BaseModel):
    name: str


class BookBody(BaseModel):
    age: int | None = Field(..., ge=2, le=4, description="Age")
    author: str = Field(None, min_length=2, max_length=4, description="Author")
    name: str


def login_required():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not request.headers.get("Authorization"):
                return {"error": "Unauthorized"}, 401
            kwargs["client_id"] = "client1234565"
            return func(*args, **kwargs)

        return wrapper

    return decorator


@pytest.fixture
def app():
    app = OpenAPI(__name__)
    app.config["TESTING"] = True

    info = Info(title="book API", version="1.0.0")
    jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    security_schemes = {"jwt": jwt}

    app = OpenAPI(__name__, info=info, security_schemes=security_schemes)
    app.config["TESTING"] = True
    security = [{"jwt": []}]

    api_view = APIView(url_prefix="/v1/books", view_tags=[Tag(name="book")], view_security=security)

    @api_view.route("")
    class BookListAPIView:
        @api_view.doc(summary="get book list", responses={204: None}, doc_ui=False)
        @login_required()
        @validate_request()
        def get(self, client_id: str):
            return {"books": ["book1", "book2"], "client_id": client_id}

        @api_view.doc(summary="create book")
        @login_required()
        @validate_request()
        def post(self, body: BookBody, client_id):
            """description for a created book"""
            return body.model_dump_json()

    @api_view.route("/<name>")
    class BookNameAPIView:
        @api_view.doc(summary="get book by name")
        @login_required()
        @validate_request()
        def get(self, path: BookNamePath, client_id):
            return {"name": path.name, "client_id": client_id}

    app.register_api_view(api_view)
    return app


@pytest.fixture
def client(app):
    client = app.test_client()

    return client


def test_get_book_list_happy(app, client):
    response = client.get("/v1/books", headers={"Authorization": "Bearer sometoken"})
    assert response.status_code == 200
    assert response.json == {"books": ["book1", "book2"], "client_id": "client1234565"}


def test_get_book_list_not_auth(app, client):
    response = client.get("/v1/books", headers={"Nope": "Bearer sometoken"})
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


def test_create_book_happy(app, client):
    response = client.post(
        "/v1/books",
        json={"age": 3, "author": "John", "name": "some_book_name"},
        headers={"Authorization": "Bearer sometoken"},
    )
    assert response.status_code == 200


def test_get_book_detail_happy(app, client):
    response = client.get("/v1/books/some_book_name", headers={"Authorization": "Bearer sometoken"})
    assert response.status_code == 200
    assert response.json == {"name": "some_book_name", "client_id": "client1234565"}

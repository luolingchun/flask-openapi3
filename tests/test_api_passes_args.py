# -*- coding: utf-8 -*-
from functools import wraps

import pytest
from flask_openapi3 import OpenAPI
from pydantic import BaseModel

app = OpenAPI(__name__)
app.config["TESTING"] = True


class GreetQuery(BaseModel):
    name: str


class GreeterService:
    def greet(self, name: str) -> str:
        return f"Hi {name}!"


def inject(fn):
    @wraps(fn)
    def _inner(*args, **kwargs):
        return fn(*args, **kwargs, greeter=GreeterService())

    return _inner


@app.get("/<version>/greet")
def view(greeter: GreeterService, query: GreetQuery):
    return greeter.greet(query.name)


app.view_functions = {k: inject(v) for k, v in app.view_functions.items()}


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_get_greeter_view(client):
    resp = client.get("/v1/greet?name=Bob")
    assert resp.status_code == 200

    assert resp.text == "Hi Bob!"

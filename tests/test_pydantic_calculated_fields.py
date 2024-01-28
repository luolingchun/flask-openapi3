# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/1/28 16:38
from functools import cached_property

import pytest
from pydantic import BaseModel, Field, computed_field

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


class User(BaseModel):
    firstName: str = Field(title="First Name")
    lastName: str

    @computed_field(title="Display Name")
    @cached_property
    def display_name(self) -> str:
        return f"{self.firstName} {self.lastName}"


@app.get("/user", responses={200: User})
def get_book():
    return "ok"


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    import pprint
    pprint.pprint(resp.json)
    assert resp.json["components"]["schemas"]["User"]["properties"].get("display_name") is not None

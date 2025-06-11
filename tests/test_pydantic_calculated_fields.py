# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/1/28 16:38
from functools import cached_property
import logging

from pydantic import BaseModel, computed_field, Field
import pytest

from flask_openapi3 import OpenAPI


logger = logging.getLogger(__name__)

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
        return f"{self.firstName} {self.lastName}"  # pragma: no cover


@app.get("/user", responses={200: User})
def get_book():
    return "ok"  # pragma: no cover


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")

    logger.info(resp.json)
    assert resp.json["components"]["schemas"]["User"]["properties"].get("display_name") is not None

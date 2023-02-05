# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/2/5 14:54

from enum import Enum

import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import Info
from flask_openapi3 import OpenAPI

app = OpenAPI(
    __name__,
    info=Info(title='Enum demo', version='1.0.0')
)

app.config["TESTING"] = True


class Language(str, Enum):
    cn = 'Chinese'
    en = 'English'


class LanguagePath(BaseModel):
    language: Language = Field(..., description='Language')


@app.get('/<language>')
def get_enum(path: LanguagePath):
    print(path)
    return {}


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    _json = resp.json
    assert resp.status_code == 200
    assert _json["components"]["schemas"].get("Language") is not None

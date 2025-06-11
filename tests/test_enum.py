# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/2/5 14:54

from enum import Enum
import logging

from pydantic import BaseModel, Field
import pytest

from flask_openapi3 import Info, OpenAPI
from flask_openapi3.request import validate_request


logger = logging.getLogger(__name__)

app = OpenAPI(__name__, info=Info(title="Enum demo", version="1.0.0"))

app.config["TESTING"] = True


class Language(str, Enum):
    cn = "Chinese"
    en = "English"


class LanguagePath(BaseModel):
    language: Language = Field(..., description="Language")


@app.get("/<language>")
@validate_request()
def get_enum(path: LanguagePath):
    logger.info(path)
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

    resp = client.get("/English")
    assert resp.status_code == 200

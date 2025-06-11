# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/12/1 9:26
import logging

from pydantic import BaseModel, Field
import pytest

from flask_openapi3 import Info, OpenAPI
from flask_openapi3.request import validate_request


logger = logging.getLogger(__name__)

info = Info(title="book API", version="1.0.0")

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True


class BookQuery(BaseModel):
    page: int = Field(1, description="current page")
    page_size: int = Field(15, description="size of per page")


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get("/book")
@validate_request()
def get_book(query: BookQuery):
    logger.info(query)
    return {"code": 0, "message": "ok"}


def test_get(client):
    resp = client.get("/book?page=2")
    logger.info(resp.json)
    assert resp.status_code == 200

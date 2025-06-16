# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/12/1 9:26
import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import Info, OpenAPI

info = Info(title='book API', version='1.0.0')

app = OpenAPI(__name__, info=info)
app.config["TESTING"] = True


class BookQuery(BaseModel):
    page: int = Field(1, description='current page')
    page_size: int = Field(15, description='size of per page')


@pytest.fixture
def client():
    client = app.test_client()

    return client


@app.get('/book')
def get_book(query: BookQuery):
    print(query)
    return {"code": 0, "message": "ok"}


def test_get(client):
    resp = client.get("/book?page=2")
    print(resp.json)
    assert resp.status_code == 200

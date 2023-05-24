# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/11/4 14:41

import pytest

from flask_openapi3 import APIView
from flask_openapi3 import OpenAPI

TEST_NUMBER = 3
TEST_KWARG = "test"

app = OpenAPI(__name__)
app.config["TESTING"] = True

api_view = APIView(url_prefix="/api/v1")


@api_view.route("/book")
class BookListAPIView:
    def __init__(self, number, kwarg=None):
        self.number = number
        self.kwarg = kwarg

    @api_view.doc(summary="get book list")
    def get(self):
        return {"number": self.number, "kwarg": self.kwarg}


app.register_api_view(api_view, view_args=[TEST_NUMBER], view_kwargs={"kwarg": TEST_KWARG})


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_get_list_view_args(client):
    resp = client.get("/api/v1/book")
    assert resp.status_code == 200

    assert resp.json["number"] == TEST_NUMBER
    assert resp.json["kwarg"] == TEST_KWARG

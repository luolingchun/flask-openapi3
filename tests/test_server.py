# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/11/10 12:17
from pydantic import ValidationError

from flask_openapi3 import Server, ServerVariable


def test_server_variable():
    Server(
        url="http://127.0.0.1:5000",
        variables=None
    )
    try:
        variables = {"one": ServerVariable(default="one", enum=[])}
        Server(
            url="http://127.0.0.1:5000",
            variables=variables
        )
        error = 0
    except ValidationError:
        error = 1
    assert error == 1
    try:
        variables = {"one": ServerVariable(default="one")}
        Server(
            url="http://127.0.0.1:5000",
            variables=variables
        )
        error = 0
    except ValidationError:
        error = 1
    assert error == 0
    try:
        variables = {"one": ServerVariable(default="one", enum=["one", "two"])}
        Server(
            url="http://127.0.0.1:5000",
            variables=variables
        )
        error = 0
    except ValidationError:
        error = 1
    assert error == 0

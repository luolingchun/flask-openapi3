# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2024/7/3 9:44
import os

import pytest

from flask_openapi3 import OpenAPI
from flask_openapi3.commands import openapi_command


@pytest.fixture
def app():
    app = OpenAPI(__name__)
    return app


@pytest.fixture
def cli_runner(app):
    return app.test_cli_runner()


def test_openapi_command(app, cli_runner):
    result = cli_runner.invoke(openapi_command, ("--output", "test.json"))
    os.remove("test.json")

    assert result.exit_code == 0
    assert "Saved to test.json." in result.output

    result = cli_runner.invoke(openapi_command, ("--format", "yaml"))

    assert result.exit_code == 0

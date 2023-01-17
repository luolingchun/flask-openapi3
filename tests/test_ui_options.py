# -*- coding: utf-8 -*-
# @Author  : bkl
# @Time    : 2023/12/18 9:23

import pytest
from pydantic import BaseModel, Extra

from flask_openapi3 import Info, OpenAPI

info = Info(title='book API', version='1.0.0')

# apply optional `ui_hide_top_bar`, `ui_favicon`, `ui_title`
app = OpenAPI(
    __name__, info=info,
    ui_hide_top_bar=True,
    ui_favicon='/static/myfavicon.ico',
    ui_title='my title test'
)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_get(client):
    print(app._app_config)
    resp = client.get("/openapi/swagger")
    data = str(resp.data)
    # print(data)
    assert resp.status_code == 200
    assert 'rel="shortcut icon" href="{}"'.format(app._app_config.get('ui_favicon')) in data
    assert '<title>{}'.format(app._app_config.get('ui_title')) in data

    if app._app_config.get('ui_hide_top_bar'):
        assert 'layout: "StandaloneLayout"' not in data


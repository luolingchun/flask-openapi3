# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/9/2 15:20
import pytest

from flask_openapi3 import OpenAPI

# Basic Authentication Sample
basic = {
    "type": "http",
    "scheme": "basic"
}
# JWT Bearer Sample
jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}
# API Key Sample
api_key = {
    "type": "apiKey",
    "name": "api_key",
    "in": "header"
}
# Implicit OAuth2 Sample
oauth2 = {
    "type": "oauth2",
    "flows": {
        "implicit": {
            "authorizationUrl": "https://example.com/api/oauth/dialog",
            "scopes": {
                "write:pets": "modify pets in your account",
                "read:pets": "read your pets"
            }
        }
    }
}
security_schemes = {"jwt": jwt, "api_key": api_key, "oauth2": oauth2, "basic": basic}
security = [{"jwt": []}]

app = OpenAPI(__name__, security_schemes=security_schemes)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi(client):
    resp = client.get("/openapi/openapi.json")
    print(resp.json)
    assert resp.status_code == 200
    assert resp.json == app.api_doc

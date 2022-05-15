import pytest
from pydantic import ValidationError

from flask_openapi3 import OpenAPI
from flask_openapi3.models import ExternalDocumentation
from openapi_python_client import GeneratorData, Config


@pytest.fixture
def app():
    _app = OpenAPI(__name__)
    _app.config["TESTING"] = True
    _app.config["VALIDATE_RESPONSE"] = True
    return _app


def test_openapi_api_doc_with_and_without_external_docs(app):
    config = Config()

    error_code = None
    try:
        ExternalDocumentation(url="example.com/openapi/markdown", description="Testing the description")
    except ValidationError as err:
        error_code = err.raw_errors[0].exc.code
    assert 'url.scheme' == error_code

    error_code = None
    try:
        ExternalDocumentation(url="/openapi/markdown", description="Testing the description")
    except ValidationError as err:
        error_code = err.raw_errors[0].exc.code
    assert 'url.scheme' == error_code

    error_code = None
    try:
        ExternalDocumentation(url="ftp://example.com/openapi/markdown", description="Testing the description")
    except ValidationError as err:
        error_code = err.raw_errors[0].exc.code
    assert 'url.scheme' == error_code

    assert "externalDocs" not in app.api_doc
    app.external_docs = ExternalDocumentation(
        url="http://example.com/openapi/markdown", description="Testing the description")
    assert "externalDocs" in app.api_doc

    openapi = GeneratorData.from_dict(data=app.api_doc, config=config)
    assert type(openapi) == GeneratorData


def test_openapi_api_doc_with_and_without_external_docs_url(app):
    client = app.test_client()
    config = Config()

    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    openapi = GeneratorData.from_dict(data=resp.json, config=config)
    assert type(openapi) == GeneratorData
    assert "externalDocs" not in resp.json

    app.external_docs = ExternalDocumentation(
        url="http://example.com/openapi/markdown", description="Testing the description")
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200
    openapi = GeneratorData.from_dict(data=resp.json, config=config)
    assert type(openapi) == GeneratorData
    assert "externalDocs" in resp.json

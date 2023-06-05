import pytest
# from openapi_python_client import GeneratorData, Config

from flask_openapi3 import OpenAPI
# from flask_openapi3 import ExternalDocumentation


@pytest.fixture
def app():
    _app = OpenAPI(__name__)
    _app.config["TESTING"] = True
    return _app


# def test_openapi_api_doc_with_and_without_external_docs(app):
#     config = Config()
#
#     ExternalDocumentation(url="example.com/openapi/markdown", description="Testing the description")
#
#     ExternalDocumentation(url="/openapi/markdown", description="Testing the description")
#
#     ExternalDocumentation(url="ftp://example.com/openapi/markdown", description="Testing the description")
#
#     assert "externalDocs" not in app.api_doc
#     app.external_docs = ExternalDocumentation(
#         url="http://example.com/openapi/markdown",
#         description="Testing the description"
#     )
#     assert "externalDocs" in app.api_doc
#
#     openapi = GeneratorData.from_dict(data=app.api_doc, config=config)
#     assert type(openapi) == GeneratorData
#
#
# def test_openapi_api_doc_with_and_without_external_docs_url(app):
#     client = app.test_client()
#     config = Config()
#
#     resp = client.get("/openapi/openapi.json")
#     assert resp.status_code == 200
#     openapi = GeneratorData.from_dict(data=resp.json, config=config)
#     assert type(openapi) == GeneratorData
#     assert "externalDocs" not in resp.json
#
#     app.external_docs = ExternalDocumentation(
#         url="http://example.com/openapi/markdown", description="Testing the description")
#     resp = client.get("/openapi/openapi.json")
#     assert resp.status_code == 200
#     openapi = GeneratorData.from_dict(data=resp.json, config=config)
#     assert type(openapi) == GeneratorData
#     assert "externalDocs" in resp.json

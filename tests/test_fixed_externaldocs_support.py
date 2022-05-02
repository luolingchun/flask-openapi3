import pytest
from flask_openapi3 import OpenAPI
from openapi_python_client import GeneratorData, Config, GeneratorError

app = OpenAPI(__name__)
app.config["TESTING"] = True
app.config["VALIDATE_RESPONSE"] = True


@pytest.fixture
def client():
    client = app.test_client()

    return client


def test_openapi_generator(client):
    config = Config()

    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200

    openapi = GeneratorData.from_dict(data=resp.json, config=config)
    assert type(openapi) == GeneratorData


def test_openapi_generator_problem_with_externaldocs_url():
    config = Config()

    openapi = GeneratorData.from_dict(data=app.api_doc, config=config)
    assert type(openapi) == GeneratorError

    # Because there are no way to check what the url_root is going to be
    # when just calling app.doc_prefix, we have to use app.doc_prefix to generate the same url
    old_doc_prefix = app.doc_prefix
    app.doc_prefix = f"http://localhost{app.doc_prefix}"

    openapi = GeneratorData.from_dict(data=app.api_doc, config=config)
    assert type(openapi) == GeneratorData

    app.doc_prefix = old_doc_prefix

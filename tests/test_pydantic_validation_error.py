import pytest
from pydantic import BaseModel, Field

from flask_openapi3 import OpenAPI

app = OpenAPI(__name__)
app.config["TESTING"] = True


@pytest.fixture
def client():
    client = app.test_client()
    return client


class LoginRequest(BaseModel):
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


@app.post("/login")
def login(body: LoginRequest):
    return {"message": f"Login successful for {body.email}"}


def test_pydantic_validation_error_schema(client):
    resp = client.get("/openapi/openapi.json")
    assert resp.status_code == 200

    schemas = resp.json["components"]["schemas"]
    assert "ValidationErrorModel" in schemas

    validation_error_schema = schemas["ValidationErrorModel"]
    properties = validation_error_schema["properties"]

    assert "type" in properties
    assert "loc" in properties
    assert "msg" in properties
    assert "input" in properties
    assert "url" in properties
    assert "ctx" in properties

    assert properties["type"]["type"] == "string"
    assert properties["loc"]["type"] == "array"
    assert properties["msg"]["type"] == "string"

    required_fields = validation_error_schema.get("required", [])
    assert "type" in required_fields
    assert "loc" in required_fields
    assert "msg" in required_fields
    assert "input" in required_fields
    assert "ctx" not in required_fields


def test_pydantic_validation_error_response(client):
    resp = client.post(
        "/login",
        json={"invalid_field": "test"},
        content_type="application/json",
    )

    assert resp.status_code == 422

    errors = resp.json
    assert isinstance(errors, list)
    assert len(errors) > 0

    error = errors[0]
    assert "type" in error
    assert "loc" in error
    assert "msg" in error
    assert "input" in error

    assert isinstance(error["type"], str)
    assert isinstance(error["loc"], list)
    assert isinstance(error["msg"], str)
    assert error["type"] in ["missing", "string_type", "value_error", "extra_forbidden"]


def test_pydantic_missing_field_error_response(client):
    resp = client.post(
        "/login",
        json={},
        content_type="application/json",
    )

    assert resp.status_code == 422

    errors = resp.json
    assert len(errors) >= 2

    email_error = None
    for error in errors:
        if error.get("loc") == ["email"]:
            email_error = error
            break

    assert email_error is not None
    assert email_error["type"] == "missing"
    assert email_error["msg"] == "Field required"
    assert email_error["input"] == {}

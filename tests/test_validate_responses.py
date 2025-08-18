from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from flask_openapi3 import APIView, OpenAPI
from flask_openapi3.blueprint import APIBlueprint


class BaseRequest(BaseModel):
    """Base description"""

    test_int: int
    test_str: str


class GoodResponse(BaseRequest): ...


class BadResponse(BaseModel):
    test_int: str
    test_str: str


def test_no_validate_response(request):
    """
    Response validation defaults to no validation
    Response doesn't match schema and doesn't raise any errors
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test", responses={201: BadResponse})
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    with test_app.test_client() as client:
        resp = client.post("/test", json={"test_int": 1, "test_str": "s"})
        assert resp.status_code == 201


def test_app_level_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name, validate_response=True)
    test_app.config["TESTING"] = True

    @test_app.post("/test", responses={201: BadResponse})
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_app_api_level_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test", responses={201: BadResponse}, validate_response=True)
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_abp_level_no_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_abp = APIBlueprint("abp", __name__)

    @test_abp.post("/test", responses={201: BadResponse})
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    test_app.register_api(test_abp)

    with test_app.test_client() as client:
        resp = client.post("/test", json={"test_int": 1, "test_str": "s"})
        assert resp.status_code == 201


def test_abp_level_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_abp = APIBlueprint("abp", __name__, validate_response=True)

    @test_abp.post("/test", responses={201: BadResponse})
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    test_app.register_api(test_abp)

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_abp_api_level_validate_response(request):
    """
    Validation turned on at app level
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_abp = APIBlueprint("abp", __name__)

    @test_abp.post("/test", responses={201: BadResponse}, validate_response=True)
    def endpoint_test(body: BaseRequest):
        return body.model_dump(), 201

    test_app.register_api(test_abp)

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_apiview_no_validate_response(request):
    """
    Response validation defaults to no validation
    Response doesn't match schema and doesn't raise any errors
    """
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_api_view = APIView("")

    @test_api_view.route("/test")
    class TestAPI:
        @test_api_view.doc(responses={201: BadResponse})
        def post(self, body: BaseRequest):
            return body.model_dump(), 201

    test_app.register_api_view(test_api_view)

    with test_app.test_client() as client:
        resp = client.post("/test", json={"test_int": 1, "test_str": "s"})
        assert resp.status_code == 201


def test_apiview_app_level_validate_response(request):
    """
    Validation turned on at app level
    """

    test_app = OpenAPI(request.node.name, validate_response=True)
    test_app.config["TESTING"] = True
    test_api_view = APIView("")

    @test_api_view.route("/test")
    class TestAPI:
        @test_api_view.doc(responses={201: BadResponse})
        def post(self, body: BaseRequest):
            return body.model_dump(), 201

    test_app.register_api_view(test_api_view)

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})


def test_apiview_api_level_validate_response(request):
    """
    Validation turned on at app level
    """

    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True
    test_api_view = APIView("")

    @test_api_view.route("/test")
    class TestAPI:
        @test_api_view.doc(responses={201: BadResponse}, validate_response=True)
        def post(self, body: BaseRequest):
            return body.model_dump(), 201

    test_app.register_api_view(test_api_view)

    with test_app.test_client() as client:
        with pytest.raises(ValidationError):
            _ = client.post("/test", json={"test_int": 1, "test_str": "s"})

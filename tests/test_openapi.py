from __future__ import annotations

from typing import Generic, TypeVar, List

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from flask_openapi3 import OpenAPI

T = TypeVar("T", bound=BaseModel)


def test_responses_are_replicated_in_open_api(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    class BaseResponse(BaseModel):
        """Base description"""
        test: int

        class Config:
            openapi_extra = {
                "description": "Custom description",
                "headers": {
                    "location": {
                        "description": "URL of the new resource",
                        "schema": {"type": "string"}
                    }
                },
                "content": {
                    "text/plain": {
                        "schema": {"type": "string"}
                    }
                },
                "links": {
                    "dummy": {
                        "description": "dummy link"
                    }
                }
            }

    @test_app.get("/test", responses={"201": BaseResponse})
    def endpoint_test():
        return b"", 201

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["201"] == {
            "description": "Custom description",
            "headers": {
                "location": {
                    "description": "URL of the new resource",
                    "schema": {"type": "string"}
                }
            },
            "content": {
                # This content is coming from responses
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/BaseResponse"}
                },
                # While this one comes from responses
                "text/plain": {
                    "schema": {"type": "string"}
                }
            },
            "links": {
                "dummy": {
                    "description": "dummy link"
                }
            }
        }


def test_none_responses_are_replicated_in_open_api(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.get(
        "/test",
        responses={
            "204": {
                "description": "Custom description",
                "headers": {
                    "x-my-special-header": {
                        "description": "Custom header",
                        "schema": {"type": "string"}
                    }
                },
                "content": {
                    "text/plain": {
                        "schema": {"type": "string"}
                    }
                },
                "links": {
                    "dummy": {
                        "description": "dummy link"
                    }
                }
            }
        }
    )
    def endpoint_test():
        return b"", 204

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["204"] == {
            "description": "Custom description",
            "headers": {
                "x-my-special-header": {
                    "description": "Custom header",
                    "schema": {"type": "string"}
                }
            },
            "content": {
                "text/plain": {
                    "schema": {"type": "string"}
                }
            },
            "links": {
                "dummy": {
                    "description": "dummy link"
                }
            }
        }


def test_responses_are_replicated_in_open_api2(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.get(
        "/test",
        responses={
            "201": {
                "description": "Custom description",
                "headers": {
                    "location": {
                        "description": "URL of the new resource",
                        "schema": {"type": "string"}
                    }
                },
                "content": {
                    "text/plain": {
                        "schema": {"type": "string"}
                    }
                },
                "links": {
                    "dummy": {
                        "description": "dummy link"
                    }
                }
            }
        }
    )
    def endpoint_test():
        return b"", 201

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["201"] == {
            "description": "Custom description",
            "headers": {
                "location": {
                    "description": "URL of the new resource",
                    "schema": {"type": "string"}
                }
            },
            "content": {
                "text/plain": {
                    "schema": {"type": "string"}
                }
            },
            "links": {
                "dummy": {
                    "description": "dummy link"
                }
            }
        }


def test_responses_without_content_are_replicated_in_open_api(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.get(
        "/test",
        responses={
            "201": {
                "description": "Custom description",
                "headers": {
                    "location": {
                        "description": "URL of the new resource",
                        "schema": {"type": "string"}
                    }
                },
                "links": {
                    "dummy": {
                        "description": "dummy link"
                    }
                }
            }
        }
    )
    def endpoint_test():
        return b"", 201

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["201"] == {
            "description": "Custom description",
            "headers": {
                "location": {
                    "description": "URL of the new resource",
                    "schema": {"type": "string"}
                }
            },
            "links": {
                "dummy": {
                    "description": "dummy link"
                }
            }
        }


class BaseRequest(BaseModel):
    """Base description"""
    test_int: int
    test_str: str


class BaseRequestGeneric(GenericModel, Generic[T]):
    detail: T


def test_body_examples_are_replicated_in_open_api(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    class Config:
        openapi_extra = {
            "examples": {
                "Example 01": {
                    "summary": "An example",
                    "value": {
                        "test_int": -1,
                        "test_str": "negative",
                    }
                },
                "Example 02": {
                    "externalValue": "https://example.org/examples/second-example.xml"
                },
                "Example 03": {
                    "$ref": "#/components/examples/third-example"
                }
            }
        }

    BaseRequestGeneric[BaseRequest].Config = Config

    @test_app.post("/test")
    def endpoint_test(body: BaseRequestGeneric[BaseRequest]):
        return body.json(), 200

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["requestBody"] == {
            "content": {
                "application/json": {
                    "examples": {
                        "Example 01": {"summary": "An example", "value": {"test_int": -1, "test_str": "negative"}},
                        "Example 02": {"externalValue": "https://example.org/examples/second-example.xml"},
                        "Example 03": {"$ref": "#/components/examples/third-example"}
                    },
                    "schema": {"$ref": "#/components/schemas/BaseRequestGeneric_BaseRequest_"}
                }
            },
            "required": True
        }
        assert resp.json["components"]["schemas"]["BaseRequestGeneric_BaseRequest_"] == {
            "properties": {"detail": {"$ref": "#/components/schemas/BaseRequest"}},
            "required": ["detail"],
            "title": "BaseRequestGeneric[BaseRequest]",
            "type": "object",
        }


def test_form_examples(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    class Config:
        openapi_extra = {
            "examples": {
                "Example 01": {
                    "summary": "An example",
                    "value": {
                        "test_int": -1,
                        "test_str": "negative",
                    }
                }
            }
        }

    BaseRequestGeneric[BaseRequest].Config = Config

    @test_app.post("/test")
    def endpoint_test(form: BaseRequestGeneric[BaseRequest]):
        return form.json(), 200

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["requestBody"] == {
            "content": {
                "multipart/form-data": {
                    "schema": {"$ref": "#/components/schemas/BaseRequestGeneric_BaseRequest_"},
                    "examples": {
                        "Example 01": {"summary": "An example", "value": {"test_int": -1, "test_str": "negative"}}
                    }
                }
            },
            "required": True
        }
        assert resp.json["components"]["schemas"]["BaseRequestGeneric_BaseRequest_"] == {
            "properties": {"detail": {"$ref": "#/components/schemas/BaseRequest"}},
            "required": ["detail"],
            "title": "BaseRequestGeneric[BaseRequest]",
            "type": "object",
        }


class BaseRequestBody(BaseModel):
    base: BaseRequest


def test_body_with_complex_object(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(body: BaseRequestBody):
        return body.json(), 200

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert {"properties", "required", "title", "type"} == set(
            resp.json["components"]["schemas"]["BaseRequestBody"].keys())


class Detail(BaseModel):
    num: int


class GenericResponse(GenericModel, Generic[T]):
    detail: T


class ListGenericResponse(GenericModel, Generic[T]):
    items: List[GenericResponse[T]]


def test_responses_with_generics(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.get("/test", responses={"201": ListGenericResponse[Detail]})
    def endpoint_test():
        return b"", 201

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["get"]["responses"]["201"] == {
            "description": "Created",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/ListGenericResponse_Detail_"}
                },
            },
        }

        schemas = resp.json["components"]["schemas"]
        detail = schemas["ListGenericResponse_Detail_"]
        assert detail["title"] == "ListGenericResponse[Detail]"
        assert detail["properties"]["items"]["items"]["$ref"] == "#/components/schemas/GenericResponse_Detail_"
        assert schemas["GenericResponse_Detail_"]["title"] == "GenericResponse[Detail]"


class PathParam(BaseModel):
    type_name: str = Field(..., description="id for path", deprecated=False, example="42", max_length=300)


def test_path_parameter_object(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(path: PathParam):
        print(path)
        return {}, 200

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["parameters"][0] == {
            "deprecated": False,
            "description": "id for path",
            "example": "42",
            "in": "path",
            "name": "type_name",
            "required": True,
            "schema": {
                "deprecated": False,
                "description": "id for path",
                "maxLength": 300,
                "example": "42",
                "title": "Type Name",
                "type": "string",
            },
        }


class QueryParam(BaseModel):
    count: int = Field(..., description="count of param", deprecated=True, example=100, le=1000.0)


def test_query_parameter_object(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(query: QueryParam):
        print(query)
        return {}, 200

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["parameters"][0] == {
            "deprecated": True,
            "description": "count of param",
            "example": 100,
            "in": "query",
            "name": "count",
            "required": True,
            "schema": {
                "deprecated": True,
                "description": "count of param",
                "maximum": 1000.0,
                "example": 100,
                "title": "Count",
                "type": "integer",
            },
        }


class HeaderParam(BaseModel):
    app_name: str = Field(None, description="app name")


class CookieParam(BaseModel):
    app_name: str = Field(None, description="app name", example="aaa")


def test_header_parameter_object(request):
    test_app = OpenAPI(request.node.name)
    test_app.config["TESTING"] = True

    @test_app.post("/test")
    def endpoint_test(header: HeaderParam, cookie: CookieParam):
        print(header)
        print(cookie)
        return {}, 200

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["parameters"][0] == {
            "description": "app name",
            "in": "header",
            "name": "app_name",
            "required": False,
            "schema": {"description": "app name", "title": "App Name", "type": "string"}
        }
        assert resp.json["paths"]["/test"]["post"]["parameters"][1] == {
            "description": "app name",
            "in": "cookie",
            "example": "aaa",
            "name": "app_name",
            "required": False,
            "schema": {"description": "app name", "example": "aaa", "title": "App Name", "type": "string"}
        }

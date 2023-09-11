from __future__ import annotations

from pydantic import BaseModel

from flask_openapi3 import OpenAPI


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
        return b'', 201

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
        return b'', 204

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
        return b'', 201

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
        return b'', 201

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

    BaseRequest.Config = Config

    @test_app.post("/test")
    def endpoint_test(body: BaseRequest):
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
                    "schema": {"$ref": "#/components/schemas/BaseRequest"}
                }
            },
            "required": True
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

    BaseRequest.Config = Config

    @test_app.post("/test")
    def endpoint_test(form: BaseRequest):
        return form.json(), 200

    with test_app.test_client() as client:
        resp = client.get("/openapi/openapi.json")
        assert resp.status_code == 200
        assert resp.json["paths"]["/test"]["post"]["requestBody"] == {
            "content": {
                "multipart/form-data": {
                    "schema": {"$ref": "#/components/schemas/BaseRequest"},
                    "examples": {
                        "Example 01": {"summary": "An example", "value": {"test_int": -1, "test_str": "negative"}}
                    }
                }
            },
            "required": True
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
        assert set(["properties", "required", "title", "type"]) == set(
            resp.json['components']['schemas']['BaseRequestBody'].keys())

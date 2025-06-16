# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/6/22 9:32

import json
from http import HTTPStatus

from flask import make_response
from pydantic import BaseModel, Field

from flask_openapi3 import Info
from flask_openapi3 import OpenAPI, APIBlueprint

app = OpenAPI(__name__, info=Info(title="Hello API", version="1.0.0"))

bp = APIBlueprint("Hello BP", __name__)


class HelloPath(BaseModel):
    name: str = Field(..., description="The name")


class Message(BaseModel):
    message: str = Field(..., description="The message")

    model_config = dict(
        openapi_extra={
            # "example": {"message": "aaa"},
            "examples": {
                "example1": {
                    "summary": "example1 summary",
                    "value": {
                        "message": "bbb"
                    }
                },
                "example2": {
                    "summary": "example2 summary",
                    "value": {
                        "message": "ccc"
                    }
                }
            }
        }
    )


@bp.get("/hello/<string:name>",
        responses={HTTPStatus.OK: Message, "201": {"content": {"text/csv": {"schema": {"type": "string"}}}}})
def hello(path: HelloPath):
    message = {"message": f"""Hello {path.name}!"""}

    response = make_response(json.dumps(message), HTTPStatus.OK)
    # response = make_response("sss", HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


@bp.get("/hello_no_response/<string:name>", responses={204: None})
def hello_no_response(path: HelloPath):
    message = {"message": f"""Hello {path.name}!"""}

    # This message will never be returned because the http code (NO_CONTENT) doesn't return anything
    response = make_response(message, HTTPStatus.NO_CONTENT)
    response.mimetype = "application/json"
    return response


app.register_api(bp)

if __name__ == "__main__":
    app.run(debug=True)

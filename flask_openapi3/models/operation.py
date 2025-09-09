# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:48

from pydantic import BaseModel

from .callback import Callback
from .external_documentation import ExternalDocumentation
from .parameter import Parameter
from .reference import Reference
from .request_body import RequestBody
from .response import Response
from .security_requirement import SecurityRequirement
from .server import Server


class Operation(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#operation-object
    """

    tags: list[str] | None = None
    summary: str | None = None
    description: str | None = None
    externalDocs: ExternalDocumentation | None = None
    operationId: str | None = None
    parameters: list[Parameter] | None = None
    requestBody: RequestBody | Reference | None = None
    responses: dict[str, Response] | None = None
    callbacks: dict[str, Callback] | None = None

    deprecated: bool | None = False
    security: list[SecurityRequirement] | None = None
    servers: list[Server] | None = None

    model_config = {"extra": "allow"}

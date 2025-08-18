# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:36
from typing import Any

from pydantic import BaseModel, Field

from .callback import Callback
from .example import Example
from .header import Header
from .link import Link
from .parameter import Parameter
from .path_item import PathItem
from .reference import Reference
from .request_body import RequestBody
from .response import Response
from .schema import Schema
from .security_scheme import SecurityScheme


class Components(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#components-object
    """

    schemas: dict[str, Reference | Schema] | None = Field(None)
    responses: dict[str, Response | Reference] | None = None
    parameters: dict[str, Parameter | Reference] | None = None
    examples: dict[str, Example | Reference] | None = None
    requestBodies: dict[str, RequestBody | Reference] | None = None
    headers: dict[str, Header | Reference] | None = None
    securitySchemes: dict[str, SecurityScheme | dict[str, Any]] | None = None
    links: dict[str, Link | Reference] | None = None
    callbacks: dict[str, Callback | Reference] | None = None
    pathItems: dict[str, PathItem | Reference] | None = None

    model_config = {"extra": "allow"}

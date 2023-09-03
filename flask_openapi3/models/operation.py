# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:48
from typing import Dict, List, Optional, Union

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

    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    externalDocs: Optional[ExternalDocumentation] = None
    operationId: Optional[str] = None
    parameters: Optional[List[Parameter]] = None
    requestBody: Optional[Union[RequestBody, Reference]] = None
    responses: Optional[Dict[str, Response]] = None
    callbacks: Optional[Dict[str, Callback]] = None

    deprecated: Optional[bool] = False
    security: Optional[List[SecurityRequirement]] = None
    servers: Optional[List[Server]] = None

    model_config = {
        "extra": "allow"
    }

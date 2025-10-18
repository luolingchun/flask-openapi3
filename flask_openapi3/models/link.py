# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:45
from typing import Any

from pydantic import BaseModel

from .server import Server


class Link(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#link-object
    """

    operationRef: str | None = None
    operationId: str | None = None
    parameters: dict[str, Any] | None = None
    requestBody: Any | None = None
    description: str | None = None
    server: Server | None = None

    model_config = {"extra": "allow"}

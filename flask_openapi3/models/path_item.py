# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:50

from pydantic import BaseModel, Field

from .operation import Operation
from .parameter import Parameter
from .reference import Reference
from .server import Server


class PathItem(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#path-item-object
    """

    ref: str | None = Field(default=None, alias="$ref")
    summary: str | None = None
    description: str | None = None
    get: Operation | None = None
    put: Operation | None = None
    post: Operation | None = None
    delete: Operation | None = None
    options: Operation | None = None
    head: Operation | None = None
    patch: Operation | None = None
    trace: Operation | None = None
    servers: list[Server] | None = None
    parameters: list[Parameter | Reference] | None = None

    model_config = {"extra": "allow", "populate_by_name": True}

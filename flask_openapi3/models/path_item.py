# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:50
import typing
from typing import Optional

from pydantic import BaseModel, Field

from .parameter import Parameter
from .reference import Reference
from .server import Server

if typing.TYPE_CHECKING:  # pragma: no cover
    from .operation import Operation


class PathItem(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#path-item-object
    """

    ref: str | None = Field(default=None, alias="$ref")
    summary: str | None = None
    description: str | None = None
    get: Optional["Operation"] = None
    put: Optional["Operation"] = None
    post: Optional["Operation"] = None
    delete: Optional["Operation"] = None
    options: Optional["Operation"] = None
    head: Optional["Operation"] = None
    patch: Optional["Operation"] = None
    trace: Optional["Operation"] = None
    servers: list[Server] | None = None
    parameters: list[Parameter | Reference] | None = None

    model_config = {"extra": "allow", "populate_by_name": True}

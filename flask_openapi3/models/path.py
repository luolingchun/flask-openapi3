# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:30
from typing import Optional, List, Dict, Union

from pydantic import BaseModel, Field

from .common import Reference, MediaType, Response
from .parameter import Parameter


class RequestBody(BaseModel):
    description: Optional[str] = None
    content: Dict[str, MediaType]
    required: Optional[bool] = Field(default=True)


class Operation(BaseModel):
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[List[Union[Parameter, Reference]]] = None
    requestBody: Optional[Union[RequestBody, Reference]] = None
    responses: Dict[str, Response] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    deprecated: Optional[bool] = None
    operationId: Optional[str] = None


class PathItem(BaseModel):
    ref: Optional[str] = Field(None, alias="$ref")
    summary: Optional[str] = None
    description: Optional[str] = None
    get: Optional[Operation] = None
    put: Optional[Operation] = None
    post: Optional[Operation] = None
    delete: Optional[Operation] = None
    options: Optional[Operation] = None
    head: Optional[Operation] = None
    patch: Optional[Operation] = None
    trace: Optional[Operation] = None

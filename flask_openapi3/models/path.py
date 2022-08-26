# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:30
from typing import Optional, List, Dict, Union

from pydantic import BaseModel, Field

from .common import Reference, MediaType, Schema
from .parameter import Parameter
from .server import Link


class RequestBody(BaseModel):
    description: Optional[str] = None
    content: Dict[str, MediaType]
    required: Optional[bool] = Field(default=True)


class Header(BaseModel):
    description: Optional[str] = None
    required: Optional[bool] = None
    schema_: Optional[Union[Schema, Reference]] = Field(None, alias="schema")


class Response(BaseModel):
    description: Optional[str]
    headers: Optional[Dict[str, Union[Header, Reference]]] = None
    content: Optional[Dict[str, MediaType]] = None
    links: Optional[Dict[str, Union[Link, Reference]]] = None

    def merge_with(self, other_response: Optional["Response"]) -> "Response":
        """Merge content from both responses."""
        if not other_response:
            return self

        if other_response.content:
            if self.content:
                self.content.update(other_response.content)
            else:
                self.content = other_response.content

        return self


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

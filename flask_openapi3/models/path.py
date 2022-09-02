# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:30
from enum import Enum
from typing import Optional, List, Dict, Union, Any

from pydantic import BaseModel, Field

from .common import Reference, MediaType, Schema, ExternalDocumentation, Example, Header
from .server import Server


class Link(BaseModel):
    operationRef: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Optional[Dict[str, Union[Any, str]]] = None
    requestBody: Optional[Union[Any, str]] = None
    description: Optional[str] = None
    server: Optional[Server] = None

    class Config:
        extra = "allow"


class RequestBody(BaseModel):
    description: Optional[str] = None
    content: Dict[str, MediaType]
    required: Optional[bool] = None

    class Config:
        extra = "allow"


class Response(BaseModel):
    description: Optional[str]
    headers: Optional[Dict[str, Union[Header, Reference]]] = None
    content: Optional[Dict[str, MediaType]] = None
    links: Optional[Dict[str, Union[Link, Reference]]] = None

    class Config:
        extra = "allow"

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


class StyleValues(str, Enum):
    matrix = "matrix"
    label = "label"
    form = "form"
    simple = "simple"
    spaceDelimited = "spaceDelimited"
    pipeDelimited = "pipeDelimited"
    deepObject = "deepObject"


class ParameterInType(str, Enum):
    query = "query"
    header = "header"
    path = "path"
    cookie = "cookie"


class Parameter(BaseModel):
    name: str
    in_: ParameterInType = Field(..., alias="in")  # ... is REQUIRED
    description: Optional[str] = None
    required: Optional[bool] = None
    deprecated: Optional[bool] = None
    allowEmptyValue: Optional[bool] = None
    # Serialization rules for simple scenarios
    style: Optional[StyleValues] = None
    explode: Optional[bool] = None
    allowReserved: Optional[bool] = None
    schema_: Optional[Union[Schema, Reference]] = Field(None, alias="schema")
    example: Optional[Any] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    # Serialization rules for more complex scenarios
    content: Optional[Dict[str, MediaType]] = None


class Operation(BaseModel):
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    externalDocs: Optional[ExternalDocumentation] = None
    operationId: Optional[str] = None
    parameters: Optional[List[Union[Parameter, Reference]]] = None
    requestBody: Optional[Union[RequestBody, Reference]] = None
    responses: Dict[str, Union[Response, Any]]
    callbacks: Optional[Dict[str, Union[Dict[str, "PathItem"], Reference]]] = None
    deprecated: Optional[bool] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    servers: Optional[List[Server]] = None

    class Config:
        extra = "allow"


class PathItem(BaseModel):
    """https://spec.openapis.org/oas/v3.0.3#path-item-object"""
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
    servers: Optional[List[Server]] = None
    parameters: Optional[List[Union[Parameter, Reference]]] = None

    class Config:
        extra = "allow"

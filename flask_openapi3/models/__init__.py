# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 10:58
from typing import Optional, List, Dict, Any, Union

from pydantic import BaseModel

from .common import ExternalDocumentation, Example, Reference, Encoding, MediaType
from .component import Components
from .info import Info
from .path import PathItem, StyleValues
from .server import Server
from .tag import Tag

OPENAPI3_REF_PREFIX = '#/components/schemas'
OPENAPI3_REF_TEMPLATE = OPENAPI3_REF_PREFIX + '/{model}'


class APISpec(BaseModel):
    """https://spec.openapis.org/oas/v3.0.3#openapi-object"""
    openapi: str
    info: Info
    servers: Optional[List[Server]] = None
    paths: Dict[str, PathItem] = None
    components: Optional[Components] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocumentation] = None

    class Config:
        extra = "allow"


class ExtraRequestBody(BaseModel):
    description: Optional[str] = None
    required: Optional[bool] = None
    # For MediaType
    example: Optional[Any] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    encoding: Optional[Dict[str, Encoding]] = None


class ExtraParameter(BaseModel):
    deprecated: Optional[bool] = None
    allowEmptyValue: Optional[bool] = None
    # Serialization rules for simple scenarios
    style: Optional[StyleValues] = None
    explode: Optional[bool] = None
    allowReserved: Optional[bool] = None
    example: Optional[Any] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    # Serialization rules for more complex scenarios
    content: Optional[Dict[str, MediaType]] = None

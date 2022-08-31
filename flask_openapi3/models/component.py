# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 11:45
from typing import Optional, Dict, Union, Any

from pydantic import BaseModel

from .common import Schema, Reference, Example, Header
from .path import Response, Parameter, RequestBody, Link, PathItem
from .security import SecurityScheme


class Components(BaseModel):
    """https://spec.openapis.org/oas/v3.0.3#components-object"""
    schemas: Optional[Dict[str, Union[Schema, Reference]]] = None
    responses: Optional[Dict[str, Union[Response, Reference]]] = None
    parameters: Optional[Dict[str, Union[Parameter, Reference]]] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    requestBodies: Optional[Dict[str, Union[RequestBody, Reference]]] = None
    headers: Optional[Dict[str, Union[Header, Reference]]] = None
    securitySchemes: Optional[Dict[str, Union[SecurityScheme, Reference]]] = None
    links: Optional[Dict[str, Union[Link, Reference]]] = None
    callbacks: Optional[Dict[str, Union[Dict[str, PathItem], Reference, Any]]] = None

    class Config:
        extra = "allow"

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 10:58
from typing import Optional, List, Dict

from pydantic import BaseModel

from .common import ExternalDocumentation
from .component import Components
from .info import Info
from .path import PathItem
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

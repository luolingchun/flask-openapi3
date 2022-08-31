# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:44
from typing import Optional

from pydantic import BaseModel

from .common import ExternalDocumentation


class Tag(BaseModel):
    """https://spec.openapis.org/oas/v3.0.3#tag-object"""
    name: str
    description: Optional[str] = None
    externalDocs: Optional[ExternalDocumentation] = None

    class Config:
        extra = "allow"

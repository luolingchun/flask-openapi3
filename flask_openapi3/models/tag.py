# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:44
from typing import Optional

from pydantic import BaseModel

from .external_documentation import ExternalDocumentation


class Tag(BaseModel):
    """
    https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#tag-object
    """

    name: str
    description: Optional[str] = None
    externalDocs: Optional[ExternalDocumentation] = None

    class Config:
        extra = "allow"

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:46
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field

from .encoding import Encoding
from .example import Example
from .reference import Reference
from .schema import Schema


class MediaType(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#media-type-object
    """

    media_type_schema: Optional[Union[Reference, Schema]] = Field(default=None, alias="schema")
    example: Optional[Any] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    encoding: Optional[Dict[str, Encoding]] = None

    class Config:
        extra = "allow"

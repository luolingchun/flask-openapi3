# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:49
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field

from .example import Example
from .media_type import MediaType
from .parameter_in_type import ParameterInType
from .reference import Reference
from .schema import Schema


class Parameter(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#parameter-object
    """

    name: str
    param_in: ParameterInType = Field(alias="in")
    description: Optional[str] = None
    required: Optional[bool] = None
    deprecated: Optional[bool] = None
    allowEmptyValue: Optional[bool] = None
    style: Optional[str] = None
    explode: Optional[bool] = None
    allowReserved: Optional[bool] = None
    param_schema: Optional[Union[Reference, Schema]] = Field(default=None, alias="schema")
    example: Optional[Any] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    content: Optional[Dict[str, MediaType]] = None

    class Config:
        extra = "allow"

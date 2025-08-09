# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:49
from typing import Any

from pydantic import BaseModel, Field

from .example import Example
from .media_type import MediaType
from .parameter_in_type import ParameterInType
from .reference import Reference
from .schema import Schema


class Parameter(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#parameter-object
    """

    name: str
    param_in: ParameterInType = Field(alias="in")
    description: str | None = None
    required: bool | None = None
    deprecated: bool | None = None
    allowEmptyValue: bool | None = None
    style: str | None = None
    explode: bool | None = None
    allowReserved: bool | None = None
    param_schema: Reference | Schema | None = Field(default=None, alias="schema")
    example: Any | None = None
    examples: dict[str, Example | Reference] | None = None
    content: dict[str, MediaType] | None = None

    model_config = {"extra": "allow", "populate_by_name": True}

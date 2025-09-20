# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:46
from typing import Any

from pydantic import BaseModel, Field

from .encoding import Encoding
from .example import Example
from .reference import Reference
from .schema import Schema


class MediaType(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#media-type-object
    """

    media_type_schema: Reference | Schema | None = Field(default=None, alias="schema")
    example: Any | None = None
    examples: dict[str, Example | Reference] | None = None
    encoding: dict[str, Encoding] | None = None

    model_config = {"extra": "allow", "populate_by_name": True}

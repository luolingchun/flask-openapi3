# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:42
from typing import Any

from pydantic import BaseModel


class Example(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#example-object
    """

    summary: str | None = None
    description: str | None = None
    value: Any | None = None
    externalValue: str | None = None

    model_config = {"extra": "allow"}

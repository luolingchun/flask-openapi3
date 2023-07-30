# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:42
from typing import Any, Optional

from pydantic import BaseModel


class Example(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#example-object
    """

    summary: Optional[str] = None
    description: Optional[str] = None
    value: Optional[Any] = None
    externalValue: Optional[str] = None

    class Config:
        extra = "allow"

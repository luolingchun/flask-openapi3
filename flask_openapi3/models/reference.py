# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:53
from pydantic import BaseModel, Field


class Reference(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#reference-object
    """

    ref: str = Field(..., alias="$ref")

    class Config:
        extra = "allow"

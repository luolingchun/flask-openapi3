# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:57

from pydantic import BaseModel, Field


class ServerVariable(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#server-variable-object
    """

    enum: list[str] | None = Field(None, min_length=1)
    default: str
    description: str | None = None

    model_config = {"extra": "allow"}

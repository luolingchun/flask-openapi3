# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:58

from pydantic import BaseModel


class XML(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#xml-object
    """

    name: str | None = None
    namespace: str | None = None
    prefix: str | None = None
    attribute: bool = False
    wrapped: bool = False

    model_config = {"extra": "allow"}

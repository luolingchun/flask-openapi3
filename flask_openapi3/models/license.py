# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:45

from pydantic import BaseModel


class License(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#license-object
    """

    name: str
    identifier: str | None = None
    url: str | None = None

    model_config = {"extra": "allow"}

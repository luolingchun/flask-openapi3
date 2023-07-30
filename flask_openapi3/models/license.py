# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:45
from typing import Optional

from pydantic import BaseModel


class License(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#license-object
    """

    name: str
    identifier: Optional[str] = None
    url: Optional[str] = None

    class Config:
        extra = "allow"

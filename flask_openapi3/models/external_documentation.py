# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:43
from typing import Optional

from pydantic import BaseModel


class ExternalDocumentation(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#external-documentation-object
    """

    description: Optional[str] = None
    url: str

    class Config:
        extra = "allow"

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:41
from typing import Dict, Optional

from pydantic import BaseModel


class Discriminator(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#discriminator-object
    """

    propertyName: str
    mapping: Optional[Dict[str, str]] = None

    class Config:
        extra = "allow"

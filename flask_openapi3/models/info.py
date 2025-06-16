# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 10:58
from typing import Optional

from pydantic import BaseModel

from .contact import Contact
from .license import License


class Info(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#info-object
    """

    title: str
    summary: Optional[str] = None
    description: Optional[str] = None
    termsOfService: Optional[str] = None
    contact: Optional[Contact] = None
    license: Optional[License] = None
    version: str

    model_config = {
        "extra": "allow"
    }

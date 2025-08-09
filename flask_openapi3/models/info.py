# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 10:58

from pydantic import BaseModel

from .contact import Contact
from .license import License


class Info(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#info-object
    """

    title: str
    summary: str | None = None
    description: str | None = None
    termsOfService: str | None = None
    contact: Contact | None = None
    license: License | None = None
    version: str

    model_config = {"extra": "allow"}

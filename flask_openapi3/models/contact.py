# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:37
from typing import Optional

from pydantic import BaseModel


class Contact(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#contact-object
    """

    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None

    class Config:
        extra = "allow"

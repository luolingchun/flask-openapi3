# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 10:58
from typing import Optional

from pydantic import BaseModel


class Contact(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    email: Optional[str] = None

    class Config:
        extra = "allow"


class License(BaseModel):
    name: str
    url: Optional[str] = None

    class Config:
        extra = "allow"


class Info(BaseModel):
    """https://spec.openapis.org/oas/v3.0.3#info-object"""
    title: str
    description: Optional[str] = None
    termsOfService: Optional[str] = None
    contact: Optional[Contact] = None
    license: Optional[License] = None
    version: str

    class Config:
        extra = "allow"

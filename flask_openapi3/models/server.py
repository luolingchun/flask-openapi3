# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:26
from typing import Optional, List, Dict

from pydantic import BaseModel


class ServerVariable(BaseModel):
    default: str
    enum: Optional[List[str]] = None
    description: Optional[str] = None

    class Config:
        extra = "allow"


class Server(BaseModel):
    """https://spec.openapis.org/oas/v3.0.3#server-object"""
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, ServerVariable]] = None

    class Config:
        extra = "allow"

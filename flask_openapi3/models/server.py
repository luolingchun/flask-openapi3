# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 11:26
from typing import Optional, List, Dict, Any

from pydantic import BaseModel


class ServerVariable(BaseModel):
    default: str
    enum: Optional[List[str]] = None
    description: Optional[str] = None


class Server(BaseModel):
    url: str
    description: Optional[str] = None
    variables: Optional[Dict[str, ServerVariable]] = None


class Link(BaseModel):
    operationRef: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    requestBody: Optional[Any] = None
    description: Optional[str] = None
    server: Optional[Server] = None

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:45
from typing import Any, Dict, Optional

from pydantic import BaseModel

from .server import Server


class Link(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#link-object
    """

    operationRef: Optional[str] = None
    operationId: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    requestBody: Optional[Any] = None
    description: Optional[str] = None
    server: Optional[Server] = None

    class Config:
        extra = "allow"

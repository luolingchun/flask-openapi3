# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:47
from typing import Dict, Optional

from pydantic import BaseModel


class OAuthFlow(BaseModel):
    """
    https://spec.openapis.org/oas/v3.0.3#oauth-flow-object
    """

    authorizationUrl: Optional[str] = None
    tokenUrl: Optional[str] = None
    refreshUrl: Optional[str] = None
    scopes: Dict[str, str]

    class Config:
        extra = "allow"

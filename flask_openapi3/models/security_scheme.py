# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:56
from typing import Optional

from pydantic import BaseModel, Field

from .oauth_flows import OAuthFlows
from .security_scheme_in_type import SecuritySchemeInType


class SecurityScheme(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#security-scheme-object
    """

    type: str
    description: Optional[str] = None
    name: Optional[str] = None
    security_scheme_in: Optional[SecuritySchemeInType] = Field(default=None, alias="in")
    scheme: Optional[str] = None
    bearerFormat: Optional[str] = None
    flows: Optional[OAuthFlows] = None
    openIdConnectUrl: Optional[str] = None

    model_config = {
        "extra": "allow"
    }

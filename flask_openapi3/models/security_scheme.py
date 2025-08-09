# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:56

from pydantic import BaseModel, Field

from .oauth_flows import OAuthFlows
from .security_scheme_in_type import SecuritySchemeInType


class SecurityScheme(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#security-scheme-object
    """

    type: str
    description: str | None = None
    name: str | None = None
    security_scheme_in: SecuritySchemeInType | None = Field(default=None, alias="in")
    scheme: str | None = None
    bearerFormat: str | None = None
    flows: OAuthFlows | None = None
    openIdConnectUrl: str | None = None

    model_config = {"extra": "allow", "populate_by_name": True}

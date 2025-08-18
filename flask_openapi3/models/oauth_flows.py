# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:47

from pydantic import BaseModel

from .oauth_flow import OAuthFlow


class OAuthFlows(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#oauth-flows-object
    """

    implicit: OAuthFlow | None = None
    password: OAuthFlow | None = None
    clientCredentials: OAuthFlow | None = None
    authorizationCode: OAuthFlow | None = None

    model_config = {"extra": "allow"}

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:47

from pydantic import BaseModel


class OAuthFlow(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#oauth-flow-object
    """

    authorizationUrl: str | None = None
    tokenUrl: str | None = None
    refreshUrl: str | None = None
    scopes: dict[str, str]

    model_config = {"extra": "allow"}

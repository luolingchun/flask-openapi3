# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:47
from typing import Optional

from pydantic import BaseModel

from .oauth_flow import OAuthFlow


class OAuthFlows(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#oauth-flows-object
    """

    implicit: Optional[OAuthFlow] = None
    password: Optional[OAuthFlow] = None
    clientCredentials: Optional[OAuthFlow] = None
    authorizationCode: Optional[OAuthFlow] = None

    model_config = {
        "extra": "allow"
    }

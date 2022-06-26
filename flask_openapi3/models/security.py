# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:12
from enum import Enum
from typing import Union, Optional, Dict

from pydantic import BaseModel, Field


class SecuritySchemeType(str, Enum):
    apiKey = "apiKey"
    http = "http"
    oauth2 = "oauth2"
    openIdConnect = "openIdConnect"


class SecurityBase(BaseModel):
    type_: SecuritySchemeType = Field(..., alias="type")
    description: Optional[str] = None


class APIKeyIn(str, Enum):
    query = "query"
    header = "header"
    cookie = "cookie"


class APIKey(SecurityBase):
    type_ = Field(default=SecuritySchemeType.apiKey, alias="type")
    in_: APIKeyIn = Field(APIKeyIn.header, alias="in")
    name: str


class HTTPBase(SecurityBase):
    type_ = Field(default=SecuritySchemeType.http, alias="type")
    scheme = 'basic'


class HTTPBearer(HTTPBase):
    scheme = "bearer"
    bearerFormat: Optional[str] = Field('JWT')


class OAuthFlow(BaseModel):
    refreshUrl: Optional[str] = None
    scopes: Dict[str, str] = {}


class OAuthFlowImplicit(OAuthFlow):
    authorizationUrl: str


class OAuthFlowPassword(OAuthFlow):
    tokenUrl: str


class OAuthFlowClientCredentials(OAuthFlow):
    tokenUrl: str


class OAuthFlowAuthorizationCode(OAuthFlow):
    authorizationUrl: str
    tokenUrl: str


class OAuthFlows(BaseModel):
    implicit: Optional[OAuthFlowImplicit] = None
    password: Optional[OAuthFlowPassword] = None
    clientCredentials: Optional[OAuthFlowClientCredentials] = None
    authorizationCode: Optional[OAuthFlowAuthorizationCode] = None


class OAuth2(SecurityBase):
    type_ = Field(default=SecuritySchemeType.oauth2, alias="type")
    flows: OAuthFlows


class OpenIdConnect(SecurityBase):
    type_ = Field(default=SecuritySchemeType.openIdConnect, alias="type")
    openIdConnectUrl: str


SecurityScheme = Union[APIKey, HTTPBase, OAuth2, OpenIdConnect, HTTPBearer]

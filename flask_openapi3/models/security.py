# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:12
import json
import warnings
from enum import Enum
from typing import Union, Optional, Dict

from pydantic import BaseModel, Field

warnings.simplefilter("once")


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

    def __new__(cls, *args, **kwargs):
        value = {
            "type": "apiKey",
            "name": "api_key",
            "in": "header"
        }
        warnings.warn(f"""\n{cls.__name__} will be deprecated in v3.x, please use \n{json.dumps(value, indent=4)} """,
                      DeprecationWarning)
        return super().__new__(cls)


class HTTPBase(SecurityBase):
    type_ = Field(default=SecuritySchemeType.http, alias="type")
    scheme = 'basic'

    def __new__(cls, *args, **kwargs):
        value = {
            "type": "http",
            "scheme": "basic"
        }
        warnings.warn(f"""\n{cls.__name__} will be deprecated in v3.x, please use \n{json.dumps(value, indent=4)} """,
                      DeprecationWarning)
        return super().__new__(cls)


class HTTPBearer(SecurityBase):
    scheme = "bearer"
    bearerFormat: Optional[str] = Field('JWT')
    type_ = Field(default=SecuritySchemeType.http, alias="type")

    def __new__(cls, *args, **kwargs):
        value = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
        warnings.warn(f"""\n{cls.__name__} will be deprecated in v3.x, please use \n{json.dumps(value, indent=4)} """,
                      DeprecationWarning)
        return super().__new__(cls)


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

    def __new__(cls, *args, **kwargs):
        value = {
            "type": "oauth2",
            "flows": {
                "implicit": {
                    "authorizationUrl": "https://example.com/api/oauth/dialog",
                    "scopes": {
                        "write:pets": "modify pets in your account",
                        "read:pets": "read your pets"
                    }
                }
            }
        }
        warnings.warn(f"""\n{cls.__name__} will be deprecated in v3.x, please use \n{json.dumps(value, indent=4)} """,
                      DeprecationWarning)
        return super().__new__(cls)


class OpenIdConnect(SecurityBase):
    type_ = Field(default=SecuritySchemeType.openIdConnect, alias="type")
    openIdConnectUrl: str

    def __new__(cls, *args, **kwargs):
        value = {
            "type": "openIdConnect",
            "openIdConnectUrl": "www.demo.com"
        }
        warnings.warn(f"""\n{cls.__name__} will be deprecated in v3.x, please use \n{json.dumps(value, indent=4)} """,
                      DeprecationWarning)
        return super().__new__(cls)


SecurityScheme = Union[APIKey, HTTPBase, OAuth2, OpenIdConnect, HTTPBearer]

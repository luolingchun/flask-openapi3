# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/28 10:58

from typing import Optional, List, Any, Dict, Union

from pydantic import BaseModel

from .callback import Callback
from .components import Components
from .contact import Contact
from .discriminator import Discriminator
from .encoding import Encoding
from .example import Example
from .external_documentation import ExternalDocumentation
from .file import FileStorage
from .header import Header
from .info import Info
from .license import License
from .link import Link
from .media_type import MediaType
from .oauth_flow import OAuthFlow
from .oauth_flows import OAuthFlows
from .operation import Operation
from .parameter import Parameter
from .parameter_in_type import ParameterInType
from .path_item import PathItem
from .paths import Paths
from .reference import Reference
from .request_body import RequestBody
from .response import Response
from .responses import Responses
from .schema import Schema
from .security_requirement import SecurityRequirement
from .security_scheme import SecurityScheme
from .server import Server
from .server_variable import ServerVariable
from .style_values import StyleValues
from .tag import Tag
from .validation_error import UnprocessableEntity
from .validation_error import ValidationErrorModel
from .xml import XML

OPENAPI3_REF_PREFIX = "#/components/schemas"
OPENAPI3_REF_TEMPLATE = OPENAPI3_REF_PREFIX + "/{model}"


class APISpec(BaseModel):
    """https://spec.openapis.org/oas/v3.0.3#openapi-object"""
    openapi: str
    info: Info
    servers: Optional[List[Server]] = None
    paths: Paths
    components: Optional[Components] = None
    security: Optional[List[SecurityRequirement]] = None
    tags: Optional[List[Tag]] = None
    externalDocs: Optional[ExternalDocumentation] = None

    class Config:
        extra = "allow"


class ExtraRequestBody(BaseModel):
    description: Optional[str] = None
    required: Optional[bool] = True
    # For MediaType
    example: Optional[Any] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    encoding: Optional[Dict[str, Encoding]] = None


class OAuthConfig(BaseModel):
    """
    https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md#oauth-20-configuration
    """
    clientId: Optional[str] = None
    clientSecret: Optional[str] = None
    realm: Optional[str] = None
    appName: Optional[str] = None
    scopeSeparator: Optional[str] = None
    scopes: Optional[str] = None
    additionalQueryStringParams: Optional[Dict[str, str]] = None
    useBasicAuthenticationWithAccessCodeGrant: Optional[bool] = False
    usePkceWithAuthorizationCodeGrant: Optional[bool] = False


PathItem.update_forward_refs(Operation=Operation)

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 10:14

__version__ = '1.1.2'

import os

from .models.file import FileStorage
from .models.info import Info
from .models.oauth import OAuthConfig
from .models.security import HTTPBase, HTTPBearer, OAuth2, APIKey, OpenIdConnect
from .models.server import Server, ServerVariable
from .models.tag import Tag
from .models.validation_error import UnprocessableEntity
from .openapi import APIBlueprint
from .openapi import OpenAPI

if os.environ.get("WERKZEUG_RUN_MAIN") is None:
    print(f" * Powered by flask-openapi3 (version: {__version__})")

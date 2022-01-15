# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 10:14

__version__ = '1.0.1'

from .models.file import FileStorage
from .models.info import Info
from .models.oauth import OAuthConfig
from .models.security import HTTPBase, HTTPBearer, OAuth2, APIKey, OpenIdConnect
from .models.server import Server, ServerVariable
from .models.tag import Tag
from .models.validation_error import UnprocessableEntity
from .openapi import APIBlueprint
from .openapi import OpenAPI

print(rf"""
         __ _           _    
        / _| |         | |   
       | |_| | __ _ ___| | __
       |  _| |/ _` / __| |/ /
       | | | | (_| \__ \   <        _  _____
       |_| |_|\__,_|___/_|\_\      (_)|____ |
  ___  _ __   ___ _ __   __ _ _ __  _     / /
 / _ \| '_ \ / _ \ '_ \ / _` | '_ \| |    \ \
| (_) | |_) |  __/ | | | (_| | |_) | |.___/ /
 \___/| .__/ \___|_| |_|\__,_| .__/|_|\____/
      | |                    | |
      |_|                    |_|
        
version: {__version__}
""")

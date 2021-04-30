# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 11:45
from typing import Optional, Dict, Union

from pydantic import BaseModel

from .common import Schema, Reference
from .security import SecurityScheme


class Components(BaseModel):
    schemas: Optional[Dict[str, Union[Schema, Reference]]] = None
    securitySchemes: Optional[Dict[str, Union[SecurityScheme, Reference]]] = None

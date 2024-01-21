# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/4/7 11:13
from enum import Enum


class SecuritySchemeInType(str, Enum):
    """The place Parameters can be put when calling an Endpoint"""

    QUERY = "query"
    HEADER = "header"
    COOKIE = "cookie"

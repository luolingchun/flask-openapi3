# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:49
from enum import Enum


class ParameterInType(str, Enum):
    """The place Parameters can be put when calling an Endpoint"""

    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    COOKIE = "cookie"

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:55

from .reference import Reference
from .response import Response

"""
https://spec.openapis.org/oas/v3.1.0#responses-object
"""
Responses = dict[str, Response | Reference]

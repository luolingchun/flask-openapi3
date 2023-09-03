# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:52
from typing import Dict

from .path_item import PathItem

"""
https://spec.openapis.org/oas/v3.1.0#paths-object
"""
Paths = Dict[str, PathItem]

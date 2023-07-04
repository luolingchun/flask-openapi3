# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/4/6 16:29
from enum import Enum


class StyleValues(str, Enum):
    matrix = "matrix"
    label = "label"
    form = "form"
    simple = "simple"
    spaceDelimited = "spaceDelimited"
    pipeDelimited = "pipeDelimited"
    deepObject = "deepObject"

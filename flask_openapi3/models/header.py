# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:44

from .parameter import Parameter
from .parameter_in_type import ParameterInType


class Header(Parameter):
    """
    https://spec.openapis.org/oas/v3.1.0#header-object
    """

    name: str | None = None  # type:ignore
    param_in: ParameterInType | None = None  # type:ignore

    model_config = {"extra": "allow"}

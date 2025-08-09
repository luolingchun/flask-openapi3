# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/9 15:25
from http import HTTPStatus
from typing import Any, Optional, Type, Union

from pydantic import BaseModel

from .models import RawModel, SecurityScheme

_ResponseDictValue = Union[Type[BaseModel], dict[Any, Any], None]

ResponseDict = dict[Union[str, int, HTTPStatus], _ResponseDictValue]

ResponseStrKeyDict = dict[str, _ResponseDictValue]

SecuritySchemesDict = dict[str, Union[SecurityScheme, dict[str, Any]]]

ParametersTuple = tuple[
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[RawModel]],
]

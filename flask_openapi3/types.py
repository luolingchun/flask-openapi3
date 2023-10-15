# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/9 15:25
from http import HTTPStatus
from typing import Dict, Union, Type, Any, Tuple, Optional

from pydantic import BaseModel

from .models import RawModel
from .models import SecurityScheme

_ResponseDictValue = Union[Type[BaseModel], Dict[Any, Any], None]

ResponseDict = Dict[Union[str, int, HTTPStatus], _ResponseDictValue]

ResponseStrKeyDict = Dict[str, _ResponseDictValue]

SecuritySchemesDict = Dict[str, Union[SecurityScheme, Dict[str, Any]]]

ParametersTuple = Tuple[
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[BaseModel]],
    Optional[Type[RawModel]]
]

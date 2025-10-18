# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/9 15:25
from http import HTTPStatus
from typing import Any, Type

from pydantic import BaseModel

from .models import RawModel, SecurityScheme

_ResponseDictValue = Type[BaseModel] | dict[Any, Any] | None

ResponseDict = dict[str | int | HTTPStatus, _ResponseDictValue]

ResponseStrKeyDict = dict[str, _ResponseDictValue]

SecuritySchemesDict = dict[str, SecurityScheme | dict[str, Any]]

ParametersTuple = tuple[
    Type[BaseModel] | None,
    Type[BaseModel] | None,
    Type[BaseModel] | None,
    Type[BaseModel] | None,
    Type[BaseModel] | None,
    Type[BaseModel] | None,
    Type[RawModel] | None,
]

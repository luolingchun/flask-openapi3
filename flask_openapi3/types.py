# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/9 15:25
from http import HTTPStatus
from typing import Any, Type, TypeVar, Union

from pydantic import BaseModel

from .models import RawModel, SecurityScheme

_MultiBaseModel = TypeVar("_MultiBaseModel", bound=Type[BaseModel])

_ResponseDictValue = Union[Type[BaseModel], _MultiBaseModel, dict[Any, Any], None]

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

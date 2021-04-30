# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 11:46
from typing import Optional, List, Any, Union, Dict

from pydantic import BaseModel, AnyUrl, Field


class ExternalDocumentation(BaseModel):
    url: AnyUrl
    description: Optional[str] = None


class Reference(BaseModel):
    ref: str = Field(..., alias="$ref")


class Schema(BaseModel):
    type_: Optional[str] = Field(None, alias="type")
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    minLength: Optional[int] = Field(None, gte=0)
    maxLength: Optional[int] = Field(None, gte=0)
    enum: Optional[List[Any]] = None
    ref: Optional[str] = Field(None, alias="$ref")


class MediaType(BaseModel):
    schema_: Optional[Union[Schema, Reference]] = Field(None, alias="schema")


class Response(BaseModel):
    description: str
    content: Optional[Dict[str, MediaType]] = None

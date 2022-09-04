# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 11:46
from typing import Optional, List, Any, Union, Dict

from pydantic import BaseModel, Field


class ExternalDocumentation(BaseModel):
    description: Optional[str] = None
    url: str

    class Config:
        extra = "allow"


class XML(BaseModel):
    name: Optional[str] = None
    namespace: Optional[str] = None
    prefix: Optional[str] = None
    attribute: Optional[bool] = None
    wrapped: Optional[bool] = None

    class Config:
        extra = "allow"


class Discriminator(BaseModel):
    propertyName: str
    mapping: Optional[Dict[str, str]] = None


class Reference(BaseModel):
    ref: str = Field(..., alias="$ref")


class Schema(BaseModel):
    ref: Optional[str] = Field(default=None, alias="$ref")
    title: Optional[str] = None
    multipleOf: Optional[float] = None
    maximum: Optional[float] = None
    exclusiveMaximum: Optional[float] = None
    minimum: Optional[float] = None
    exclusiveMinimum: Optional[float] = None
    maxLength: Optional[int] = Field(default=None, gte=0)
    minLength: Optional[int] = Field(default=None, gte=0)
    pattern: Optional[str] = None
    maxItems: Optional[int] = Field(default=None, gte=0)
    minItems: Optional[int] = Field(default=None, gte=0)
    uniqueItems: Optional[bool] = None
    maxProperties: Optional[int] = Field(default=None, gte=0)
    minProperties: Optional[int] = Field(default=None, gte=0)
    required: Optional[List[str]] = None
    enum: Optional[List[Any]] = None
    type: Optional[str] = None
    allOf: Optional[List["Schema"]] = None
    oneOf: Optional[List["Schema"]] = None
    anyOf: Optional[List["Schema"]] = None
    not_: Optional["Schema"] = Field(default=None, alias="not")
    items: Optional[Union["Schema", List["Schema"]]] = None
    properties: Optional[Dict[str, "Schema"]] = None
    additionalProperties: Optional[Union["Schema", Reference, bool]] = None
    description: Optional[str] = None
    format: Optional[str] = None
    default: Optional[Any] = None
    nullable: Optional[bool] = None
    discriminator: Optional[Discriminator] = None
    readOnly: Optional[bool] = None
    writeOnly: Optional[bool] = None
    xml: Optional[XML] = None
    externalDocs: Optional[ExternalDocumentation] = None
    example: Optional[Any] = None
    deprecated: Optional[bool] = None


class Example(BaseModel):
    summary: Optional[str] = None
    description: Optional[str] = None
    value: Optional[Any] = None
    externalValue: Optional[str] = None

    class Config:
        extra = "allow"


class Encoding(BaseModel):
    contentType: Optional[str] = None
    headers: Optional[Dict[str, Union["Header", Reference]]] = None
    style: Optional[str] = None
    explode: Optional[bool] = None
    allowReserved: Optional[bool] = None

    class Config:
        extra = "allow"


class MediaType(BaseModel):
    schema_: Optional[Union[Schema, Reference]] = Field(None, alias="schema")
    example: Optional[Any] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    encoding: Optional[Dict[str, Encoding]] = None

    class Config:
        extra = "allow"


class Header(BaseModel):
    description: Optional[str] = None
    required: Optional[bool] = None
    deprecated: Optional[bool] = None
    # Serialization rules for simple scenarios
    style: Optional[str] = None
    explode: Optional[bool] = None
    allowReserved: Optional[bool] = None
    schema_: Optional[Union[Schema, Reference]] = Field(default=None, alias="schema")
    example: Optional[Any] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    # Serialization rules for more complex scenarios
    content: Optional[Dict[str, MediaType]] = None

    class Config:
        extra = "allow"


class ExtraRequestBody(BaseModel):
    description: Optional[str] = None
    required: Optional[bool] = None
    # For MediaType
    example: Optional[Any] = None
    examples: Optional[Dict[str, Union[Example, Reference]]] = None
    encoding: Optional[Dict[str, Encoding]] = None

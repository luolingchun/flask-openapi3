# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2023/7/4 9:55
from typing import Any, Union

from pydantic import BaseModel, Field

from .data_type import DataType
from .discriminator import Discriminator
from .external_documentation import ExternalDocumentation
from .reference import Reference
from .xml import XML


class Schema(BaseModel):
    """
    https://spec.openapis.org/oas/v3.1.0#schema-object
    """

    ref: str | None = Field(alias="$ref", default=None)
    title: str | None = None
    multipleOf: float | None = Field(default=None, gt=0.0)
    maximum: int | float | None = None
    exclusiveMaximum: float | None = None
    minimum: float | None = None
    exclusiveMinimum: float | None = None
    maxLength: int | None = Field(default=None, ge=0)
    minLength: int | None = Field(default=None, ge=0)
    pattern: str | None = None
    maxItems: int | None = Field(default=None, ge=0)
    minItems: int | None = Field(default=None, ge=0)
    uniqueItems: bool | None = None
    maxProperties: int | None = Field(default=None, ge=0)
    minProperties: int | None = Field(default=None, ge=0)
    required: list[str] | None = Field(default=None)
    enum: None | list[Any] = Field(default=None)
    type: DataType | None = Field(default=None)
    allOf: list[Union[Reference, "Schema"]] | None = None
    oneOf: list[Union[Reference, "Schema"]] | None = None
    anyOf: list[Union[Reference, "Schema"]] | None = None
    schema_not: Union[Reference, "Schema"] | None = Field(default=None, alias="not")
    items: Union[Reference, "Schema"] | None = None
    properties: dict[str, Union[Reference, "Schema"]] | None = None
    prefixItems: list[Union[Reference, "Schema"]] | None = None
    additionalProperties: Union[bool, Reference, "Schema"] | None = None
    description: str | None = None
    schema_format: str | None = Field(default=None, alias="format")
    default: Any | None = None
    nullable: bool | None = None
    discriminator: Discriminator | None = None
    readOnly: bool | None = None
    writeOnly: bool | None = None
    xml: XML | None = None
    externalDocs: ExternalDocumentation | None = None
    example: Any | None = None
    deprecated: bool | None = None
    const: str | None = None

    model_config = {"populate_by_name": True}

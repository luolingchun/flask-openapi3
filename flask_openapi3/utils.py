# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/1 21:34
import inspect

from pydantic import BaseModel
from werkzeug.routing import parse_rule

from flask_openapi3.models import OPENAPI3_REF_TEMPLATE, Tag
from flask_openapi3.models.common import Schema, Response, MediaType
from flask_openapi3.models.parameter import ParameterInType, Parameter
from flask_openapi3.models.path import Operation

SCHEMA_TYPES = {
    "default": "string",
    "string": "string",
    "any": "string",
    "path": "string",
    "int": "integer",
    "float": "number",
    "uuid": "string",
}


def _parse_rule(rule):
    """parse route"""
    uri = ''
    for converter, args, variable in parse_rule(str(rule)):
        # print(converter, args, variable)
        if converter is None:
            uri += variable
            continue
        uri += "{%s}" % variable
    return uri


def get_operation(func, tags=None):
    if tags is None:
        tags = []
    # get func documents
    doc = inspect.getdoc(func) or ''
    operation = Operation(
        tags=[tag.name if isinstance(tag, Tag) else tag for tag in tags],
        summary=doc.split('\n')[0],
        description=doc.split('\n')[-1]
    )

    return operation


def get_func_parameters(func, arg_name='path'):
    """get func parameters"""
    signature = inspect.signature(func)
    return signature.parameters.get(arg_name)


def get_schema(obj):
    obj = obj.annotation
    assert issubclass(obj, BaseModel), "invalid `pedantic.BaseModel`"
    return obj.schema(ref_template=OPENAPI3_REF_TEMPLATE)


def parse_path(path):
    """parse args(path)"""
    schema = get_schema(path)
    parameters = []
    properties = schema.get('properties')

    if properties:
        for name, value in properties.items():
            data = {
                "name": name,
                "in": ParameterInType.path,
                "description": value.get("description"),
                "required": True,
                "schema": Schema(**value)
            }
            parameters.append(Parameter(**data))

    return parameters


def parse_query(query):
    schema = get_schema(query)
    parameters = []
    schemas = dict()
    properties = schema.get('properties')
    definitions = schema.get('definitions')

    if properties:
        for name, value in properties.items():
            data = {
                "name": name,
                "in": ParameterInType.query,
                "description": value.get("description"),
                "required": name in schema.get("required", []),
                "schema": Schema(**value)
            }
            parameters.append(Parameter(**data))
    if definitions:
        for name, value in definitions.items():
            schemas[name] = Schema(**value)
    return parameters, schemas


def get_responses(response):
    responses = []
    schemas = {}
    if response:
        assert issubclass(response, BaseModel), "invalid `pedantic.BaseModel`"
        schema = response.schema(ref_template=OPENAPI3_REF_TEMPLATE)
        responses = {
            "200": Response(
                description="Success",
                content={
                    "application/json": MediaType(
                        **{
                            "schema": Schema(
                                **{
                                    "$ref": f"#/components/schemas/{response.__name__}"
                                }
                            )
                        }
                    )
                }
            ),
            "422": Response(description="Validation error"),
            "500": Response(description='Server error')}
        schemas[response.__name__] = Schema(**schema)
        definitions = schema.get('definitions')
        if definitions:
            for name, value in definitions.items():
                schemas[name] = Schema(**value)

    return responses, schemas

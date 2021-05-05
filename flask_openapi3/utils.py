# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/1 21:34
import inspect

from pydantic import BaseModel
from werkzeug.routing import parse_rule

from flask_openapi3.models import openapi3_ref_template
from flask_openapi3.models.common import Schema
from flask_openapi3.models.parameter import ParameterInType, Parameter

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
    uri = ''
    for converter, args, variable in parse_rule(str(rule)):
        # print(converter, args, variable)
        if converter is None:
            uri += variable
            continue
        uri += "{%s}" % variable
    return uri


def get_func_parameters(func):
    signature = inspect.signature(func)
    return signature.parameters


def _get_schema(obj):
    obj = obj.annotation
    assert issubclass(obj, BaseModel)
    return obj.schema(ref_template=openapi3_ref_template)


def _parse_path(path):
    schema = _get_schema(path)
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


def _parse_query(query):
    schema = _get_schema(query)
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

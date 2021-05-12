# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/1 21:34
import inspect

from pydantic import BaseModel
from werkzeug.routing import parse_rule

from .models import OPENAPI3_REF_TEMPLATE, OPENAPI3_REF_PREFIX
from .models.common import Schema, Response, MediaType
from .models.parameter import ParameterInType, Parameter
from .models.path import Operation
from .models.validation_error import UnprocessableEntity


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


def get_operation(func):
    # get func documents
    doc = inspect.getdoc(func) or ''
    operation = Operation(
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


def parse_header(header):
    """parse args(header)"""
    schema = get_schema(header)
    parameters = []
    properties = schema.get('properties')

    if properties:
        for name, value in properties.items():
            data = {
                "name": name,
                "in": ParameterInType.header,
                "description": value.get("description"),
                "required": name in schema.get("required", []),
                "schema": Schema(**value)
            }
            parameters.append(Parameter(**data))

    return parameters


def parse_cookie(cookie):
    """parse args(cookie)"""
    schema = get_schema(cookie)
    parameters = []
    properties = schema.get('properties')

    if properties:
        for name, value in properties.items():
            data = {
                "name": name,
                "in": ParameterInType.cookie,
                "description": value.get("description"),
                "required": name in schema.get("required", []),
                "schema": Schema(**value)
            }
            parameters.append(Parameter(**data))

    return parameters


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
    components_schemas = dict()
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
            components_schemas[name] = Schema(**value)
    return parameters, components_schemas


def parse_form(form):
    schema = get_schema(form)
    content = None
    components_schemas = dict()
    properties = schema.get('properties')
    definitions = schema.get('definitions')

    if properties:
        title = schema.get('title')
        components_schemas[title] = Schema(**schema)
        content = {
            "multipart/form-data": MediaType(
                **{
                    "schema": Schema(
                        **{
                            "$ref": f"{OPENAPI3_REF_PREFIX}/{title}"
                        }
                    )
                }
            )
        }
    if definitions:
        for name, value in definitions.items():
            components_schemas[name] = Schema(**value)
    return content, components_schemas


def parse_json(json):
    schema = get_schema(json)
    content = None
    components_schemas = dict()
    properties = schema.get('properties')
    definitions = schema.get('definitions')

    if properties:
        title = schema.get('title')
        components_schemas[title] = Schema(**schema)
        content = {
            "application/json": MediaType(
                **{
                    "schema": Schema(
                        **{
                            "$ref": f"{OPENAPI3_REF_PREFIX}/{title}"
                        }
                    )
                }
            )
        }
    if definitions:
        for name, value in definitions.items():
            components_schemas[name] = Schema(**value)
    return content, components_schemas


def get_responses(responses: dict):
    _responses = {}
    _schemas = {}
    if not responses.get("422"):
        _responses["422"] = Response(
            description="HTTP Validation error",
            content={
                "application/json": MediaType(
                    **{
                        "schema": Schema(
                            **{
                                "type": "array",
                                "items": {"$ref": f"{OPENAPI3_REF_PREFIX}/{UnprocessableEntity.__name__}"}
                            }
                        )
                    }
                )
            }
        )
        _schemas[UnprocessableEntity.__name__] = Schema(**UnprocessableEntity.schema())
    if not responses.get("500"):
        _responses["500"] = Response(description='Server error')
    for key, response in responses.items():
        assert issubclass(response, BaseModel), "invalid `pedantic.BaseModel`"
        schema = response.schema(ref_template=OPENAPI3_REF_TEMPLATE)
        _responses[key] = Response(
            description="Success",
            content={
                "application/json": MediaType(
                    **{
                        "schema": Schema(
                            **{
                                "$ref": f"{OPENAPI3_REF_PREFIX}/{response.__name__}"
                            }
                        )
                    }
                )
            }
        )
        _schemas[response.__name__] = Schema(**schema)
        definitions = schema.get('definitions')
        if definitions:
            for name, value in definitions.items():
                _schemas[name] = Schema(**value)

    return _responses, _schemas

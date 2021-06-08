# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/1 21:34
import inspect
from typing import Dict, Type, Callable, List, Tuple, Any

from pydantic import BaseModel
from werkzeug.routing import parse_rule

from .models import OPENAPI3_REF_TEMPLATE, OPENAPI3_REF_PREFIX, Tag
from .models.common import Schema, Response, MediaType
from .models.parameter import ParameterInType, Parameter
from .models.path import Operation, RequestBody, PathItem
from .models.validation_error import UnprocessableEntity


def _parse_rule(rule: str) -> str:
    """parse route"""
    uri = ''
    for converter, args, variable in parse_rule(str(rule)):
        if converter is None:
            uri += variable
            continue
        uri += "{%s}" % variable
    return uri


def get_operation(func: Callable) -> Operation:
    # get func documents
    doc = inspect.getdoc(func) or ''
    doc = doc.strip()
    lines = doc.split('\n')
    operation = Operation(
        summary=lines[0] or None,
        description=lines[0] if len(lines) == 0 else '</br>'.join(lines[1:]) or None
    )

    return operation


def get_func_parameter(func: Callable, arg_name='path') -> Type[BaseModel]:
    """get func parameters"""
    signature = inspect.signature(func)
    p = signature.parameters.get(arg_name)
    return p.annotation if p else None


def get_schema(obj: Type[BaseModel]) -> dict:
    assert inspect.isclass(obj) and \
           issubclass(obj, BaseModel), f"{obj} is invalid `pydantic.BaseModel`"
    return obj.schema(ref_template=OPENAPI3_REF_TEMPLATE)


def parse_header(header: Type[BaseModel]) -> List[Parameter]:
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


def parse_cookie(cookie: Type[BaseModel]) -> List[Parameter]:
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


def parse_path(path: Type[BaseModel]) -> List[Parameter]:
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


def parse_query(query: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
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


def parse_form(form: Type[BaseModel]) -> Tuple[Dict[str, MediaType], dict]:
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


def parse_body(body: Type[BaseModel]) -> Tuple[Dict[str, MediaType], dict]:
    schema = get_schema(body)
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


def get_responses(responses: dict, components_schemas: dict, operation: Operation) -> None:
    """
    :param responses: Dict[str, BaseModel]
    :param components_schemas: `models.component.py` Components.schemas
    :param operation: `models.path.py` Operation
    """
    if responses is None:
        responses = {}
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
        assert inspect.isclass(response) and \
               issubclass(response, BaseModel), f" {response} is invalid `pydantic.BaseModel`"
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

    components_schemas.update(**_schemas)
    operation.responses = _responses


def validate_responses(responses: Dict[str, Type[BaseModel]]) -> None:
    if responses is None:
        responses = {}
    assert isinstance(responses, dict), "invalid `dict`"


def validate_response(resp: Any, responses: Dict[str, Type[BaseModel]]) -> None:
    """validate response(only validate 200)"""
    if responses is None:
        responses = {}
    for key, response in responses.items():
        if key != "200":
            continue
        assert inspect.isclass(response) and \
               issubclass(response, BaseModel), f"{response} is invalid `pydantic.BaseModel`"
        _resp = resp
        if isinstance(resp, tuple):  # noqa
            _resp = resp[0]
        response(**_resp)


def parse_and_store_tags(
        new_tags: List[Tag] = None,
        old_tags: List[Tag] = None,
        old_tag_names: List[str] = None,
        operation: Operation = None
) -> None:
    """store tags
    :param new_tags: api tag
    :param old_tags: openapi doc tags
    :param old_tag_names: openapi doc tag names
    :param operation: `models.path.py` Operation
    """
    if new_tags is None:
        new_tags = []
    for tag in new_tags:
        if tag.name not in old_tag_names:
            old_tag_names.append(tag.name)
            old_tags.append(tag)
    operation.tags = list(set([tag.name for tag in new_tags])) or None


def parse_parameters(
        func: Callable,
        components_schemas: dict,
        operation: Operation
) -> Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel]]:
    """
    :param func: flask view func
    :param components_schemas: `models.component.py` Components.schemas
    :param operation: `models.path.py` Operation
    """
    parameters = []
    header = get_func_parameter(func, 'header')
    cookie = get_func_parameter(func, 'cookie')
    path = get_func_parameter(func, 'path')
    query = get_func_parameter(func, 'query')
    form = get_func_parameter(func, 'form')
    body = get_func_parameter(func, 'body')
    if header:
        _parameters = parse_header(header)
        parameters.extend(_parameters)
    if cookie:
        _parameters = parse_cookie(cookie)
        parameters.extend(_parameters)
    if path:
        # get args from route path
        _parameters = parse_path(path)
        parameters.extend(_parameters)
    if query:
        # get args from route query
        _parameters, _components_schemas = parse_query(query)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)
    if form:
        _content, _components_schemas = parse_form(form)
        components_schemas.update(**_components_schemas)
        requestBody = RequestBody(**{
            "content": _content,
        })
        operation.requestBody = requestBody
    if body:
        _content, _components_schemas = parse_body(body)
        components_schemas.update(**_components_schemas)
        requestBody = RequestBody(**{
            "content": _content,
        })
        operation.requestBody = requestBody
    operation.parameters = parameters if parameters else None

    return header, cookie, path, query, form, body


def parse_method(uri: str, method: str, paths: dict, operation: Operation) -> None:
    """
    :param uri: api route path
    :param method: get post put delete patch
    :param paths: openapi doc paths
    :param operation: `models.path.py` Operation
    """
    if method == 'get':
        if not paths.get(uri):
            paths[uri] = PathItem(get=operation)
        else:
            paths[uri].get = operation
    elif method == 'post':
        if not paths.get(uri):
            paths[uri] = PathItem(post=operation)
        else:
            paths[uri].post = operation
    elif method == 'put':
        if not paths.get(uri):
            paths[uri] = PathItem(put=operation)
        else:
            paths[uri].put = operation
    elif method == 'patch':
        if not paths.get(uri):
            paths[uri] = PathItem(patch=operation)
        else:
            paths[uri].patch = operation
    elif method == 'delete':
        if not paths.get(uri):
            paths[uri] = PathItem(delete=operation)
        else:
            paths[uri].delete = operation

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/1 21:34

import inspect
import re
from http import HTTPStatus
from typing import Dict, Type, Callable, List, Tuple, Any, ForwardRef

import pydantic.typing
from flask import Response as _Response, current_app
from pydantic import BaseModel

from .http import HTTP_STATUS, HTTPMethod
from .models import OPENAPI3_REF_TEMPLATE, OPENAPI3_REF_PREFIX, Tag
from .models.common import Schema, Response, MediaType
from .models.parameter import ParameterInType, Parameter
from .models.path import Operation, RequestBody, PathItem
from .models.validation_error import UnprocessableEntity


def get_operation(func: Callable, *, summary: str = None, description: str = None) -> Operation:
    """Return an Operation object with summary and description."""
    doc = inspect.getdoc(func) or ""
    doc = doc.strip()
    lines = doc.split("\n")
    doc_summary = lines[0] or None
    if summary is None:
        doc_description = lines[0] if len(lines) == 0 else "</br>".join(lines[1:]) or None
    else:
        doc_description = "</br>".join(lines) or None
    operation = Operation(
        summary=summary or doc_summary,
        description=description or doc_description
    )

    return operation


def get_operation_id_for_path(*, name: str, path: str, method: str) -> str:
    operation_id = name + path
    operation_id = re.sub(r"\W", "_", operation_id)
    operation_id = operation_id + "_" + method.lower()
    return operation_id


def get_func_parameter(func: Callable, *, parameter_name="path") -> Type[BaseModel]:
    """Get view-func parameters.
    parameter_name has six parameters to choose from: path, query, form, body, header, cookie.
    """
    signature = inspect.signature(func)
    param = signature.parameters.get(parameter_name)
    annotation = param.annotation if param else None
    if isinstance(annotation, str):
        # PEP563
        while hasattr(func, "__wrapped__"):
            # Find globalns for the unwrapped func.
            func = func.__wrapped__
        globalns = getattr(func, "__globals__", {})
        annotation = ForwardRef(annotation)
        annotation = pydantic.typing.evaluate_forwardref(annotation, globalns, globalns)
    return annotation


def get_schema(obj: Type[BaseModel]) -> dict:
    """Pydantic model conversion to openapi schema"""
    assert inspect.isclass(obj) and \
           issubclass(obj, BaseModel), f"{obj}{type(obj)} is invalid `pydantic.BaseModel`"

    return obj.schema(ref_template=OPENAPI3_REF_TEMPLATE)


def parse_header(header: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parse header model"""
    schema = get_schema(header)
    parameters = []
    components_schemas = dict()
    properties = schema.get("properties", {})
    definitions = schema.get("definitions", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.header,
            "description": value.get("description"),
            "required": name in schema.get("required", []),
            "schema": Schema(**value)
        }
        parameters.append(Parameter(**data))

    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_cookie(cookie: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parse cookie model"""
    schema = get_schema(cookie)
    parameters = []
    components_schemas = dict()
    properties = schema.get("properties", {})
    definitions = schema.get("definitions", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.cookie,
            "description": value.get("description"),
            "required": name in schema.get("required", []),
            "schema": Schema(**value)
        }
        parameters.append(Parameter(**data))

    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_path(path: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parse path model"""
    schema = get_schema(path)
    parameters = []
    components_schemas = dict()
    properties = schema.get("properties", {})
    definitions = schema.get("definitions", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.path,
            "description": value.get("description"),
            "required": True,
            "schema": Schema(**value)
        }
        parameters.append(Parameter(**data))

    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_query(query: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parse query model"""
    schema = get_schema(query)
    parameters = []
    components_schemas = dict()
    properties = schema.get("properties", {})
    definitions = schema.get("definitions", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.query,
            "description": value.get("description"),
            "required": name in schema.get("required", []),
            "schema": Schema(**value)
        }
        parameters.append(Parameter(**data))

    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_form(form: Type[BaseModel]) -> Tuple[Dict[str, MediaType], dict]:
    """Parse form model"""
    schema = get_schema(form)
    components_schemas = dict()
    properties = schema.get("properties", {})
    definitions = schema.get("definitions", {})

    assert properties, f"{form.__name__}'s properties cannot be empty."

    title = schema.get("title")
    components_schemas[title] = Schema(**schema)
    encoding = {}
    for k, v in properties.items():
        if v.get("type") == "array":
            encoding[k] = {"style": "form"}

    content = {
        "multipart/form-data": MediaType(
            **{
                "schema": Schema(
                    **{
                        "$ref": f"{OPENAPI3_REF_PREFIX}/{title}"
                    }
                ),
                "encoding": encoding
            }
        )
    }

    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return content, components_schemas


def parse_body(body: Type[BaseModel]) -> Tuple[Dict[str, MediaType], dict]:
    """Parse body model"""
    schema = get_schema(body)
    components_schemas = dict()
    definitions = schema.get("definitions", {})

    title = schema.get("title")
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

    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return content, components_schemas


def get_responses(
        responses: dict,
        extra_responses: Dict[str, dict],
        components_schemas: dict,
        operation: Operation
) -> None:
    """
    :param responses: Dict[str, BaseModel]
    :param extra_responses: Dict[str, dict]
    :param components_schemas: `models.component.py` `Components.schemas`
    :param operation: `models.path.py` Operation
    """
    if responses is None:
        responses = {}
    _responses = {}
    _schemas = {}
    if not responses.get("422"):
        _responses["422"] = Response(
            description=HTTP_STATUS["422"],
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
    for key, response in responses.items():
        # Verify that the response is a class and that class is a subclass of `pydantic.BaseModel`
        if inspect.isclass(response) and issubclass(response, BaseModel):
            schema = response.schema(ref_template=OPENAPI3_REF_TEMPLATE)
            _responses[key] = Response(
                description=HTTP_STATUS.get(key, ""),
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
            definitions = schema.get("definitions")
            if definitions:
                for name, value in definitions.items():
                    _schemas[name] = Schema(**value)
        # Verify that if the response is None, because http status code "204" means return "No Content"
        elif response is None:
            _responses[key] = Response(
                description=HTTP_STATUS.get(key, ""),
            )
        else:
            raise TypeError(f"{response} is invalid `pydantic.BaseModel`.")
    # handle extra_responses
    for key, value in extra_responses.items():
        # key "200" value {"content":{"text/csv":{"schema":{"type": "string"}}}}
        extra_content = value.get("content", {})
        if extra_content:
            # {"text/csv":{"schema":{"type": "string"}}}
            if _responses.get(key) and isinstance(extra_content, dict):
                _responses[key].content.update(**extra_content)  # noqa
            else:
                _responses[key] = Response(
                    description=HTTP_STATUS.get(key, ""),
                    content=extra_content
                )

    components_schemas.update(**_schemas)
    operation.responses = _responses


def validate_responses_type(responses: Dict[str, Any]) -> None:
    assert isinstance(responses, dict), f"{responses} invalid `dict`"


def validate_response(resp: Any, responses: Dict[str, Type[BaseModel]]) -> None:
    """Validate response"""
    if not current_app.config.get("FLASK_OPENAPI_DISABLE_WARNINGS", False):
        print("Warning: "
              "You are using `FLASK_OPENAPI_VALIDATE_RESPONSE=True`, "
              "please do not use it in the production environment, "
              "because it will reduce the performance. "
              "Note, you can disable this warning with `Flask.config['FLASK_OPENAPI_DISABLE_WARNINGS'] = True`")
    if isinstance(resp, tuple):  # noqa
        _resp, status_code = resp[:2]
    elif isinstance(resp, _Response):
        if resp.mimetype != "application/json":
            # only application/json
            return
            # raise TypeError("`Response` mimetype must be application/json.")
        _resp, status_code = resp.json, resp.status_code  # noqa
    else:
        _resp, status_code = resp, 200
    # status_code is http.HTTPStatus
    if isinstance(status_code, HTTPStatus):
        status_code = status_code.value

    resp_model = responses.get(str(status_code))
    if resp_model is None:
        return
    assert inspect.isclass(resp_model) and \
           issubclass(resp_model, BaseModel), f"{resp_model} is invalid `pydantic.BaseModel`"
    try:
        if resp_model.__custom_root_type__:
            # https://pydantic-docs.helpmanual.io/usage/models/#custom-root-types
            resp_model(__root__=_resp)
        else:
            resp_model(**_resp)
    except TypeError:
        raise TypeError(f"`{resp_model.__name__}` validation failed, must be a mapping.")


def parse_and_store_tags(
        new_tags: List[Tag] = None,
        old_tags: List[Tag] = None,
        old_tag_names: List[str] = None,
        operation: Operation = None
) -> None:
    """Store tags
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
        *,
        components_schemas: dict = None,
        operation: Operation = None,
        doc_ui: bool = True,
) -> Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel]]:
    """
    :param func: flask view func
    :param components_schemas: `models.component.py` Components.schemas
    :param operation: `models.path.py` Operation
    :param doc_ui: add openapi document UI(swagger and redoc). Defaults to True.
    """
    parameters = []
    header = get_func_parameter(func, parameter_name="header")
    cookie = get_func_parameter(func, parameter_name="cookie")
    path = get_func_parameter(func, parameter_name="path")
    query = get_func_parameter(func, parameter_name="query")
    form = get_func_parameter(func, parameter_name="form")
    body = get_func_parameter(func, parameter_name="body")
    if doc_ui is False:
        return header, cookie, path, query, form, body
    if header:
        _parameters, _components_schemas = parse_header(header)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)
    if cookie:
        _parameters, _components_schemas = parse_cookie(cookie)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)
    if path:
        # get args from route path
        _parameters, _components_schemas = parse_path(path)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)
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
    if method == HTTPMethod.GET:
        if not paths.get(uri):
            paths[uri] = PathItem(get=operation)
        else:
            paths[uri].get = operation
    elif method == HTTPMethod.POST:
        if not paths.get(uri):
            paths[uri] = PathItem(post=operation)
        else:
            paths[uri].post = operation
    elif method == HTTPMethod.PUT:
        if not paths.get(uri):
            paths[uri] = PathItem(put=operation)
        else:
            paths[uri].put = operation
    elif method == HTTPMethod.PATCH:
        if not paths.get(uri):
            paths[uri] = PathItem(patch=operation)
        else:
            paths[uri].patch = operation
    elif method == HTTPMethod.DELETE:
        if not paths.get(uri):
            paths[uri] = PathItem(delete=operation)
        else:
            paths[uri].delete = operation

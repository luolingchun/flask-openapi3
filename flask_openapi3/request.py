# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/1 16:54
import inspect
import json
from functools import wraps
from json import JSONDecodeError
from typing import Any, Type

from flask import abort, current_app, request
from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo
from werkzeug.datastructures.structures import MultiDict

from .utils import parse_parameters


def _get_list_value(model: Type[BaseModel], args: MultiDict, model_field_key: str, model_field_value: FieldInfo):
    if model_field_value.alias and model.model_config.get("populate_by_name"):
        key = model_field_value.alias
        value = args.getlist(model_field_value.alias) or args.getlist(model_field_key)
    elif model_field_value.alias:
        key = model_field_value.alias
        value = args.getlist(model_field_value.alias)
    else:
        key = model_field_key
        value = args.getlist(model_field_key)

    return key, value


def _get_value(model: Type[BaseModel], args: MultiDict, model_field_key: str, model_field_value: FieldInfo):
    if model_field_value.alias and model.model_config.get("populate_by_name"):
        key = model_field_value.alias
        value = args.get(model_field_value.alias) or args.get(model_field_key)
    elif model_field_value.alias:
        key = model_field_value.alias
        value = args.get(model_field_value.alias)
    else:
        key = model_field_key
        value = args.get(model_field_key)

    return key, value


def _validate_header(header: Type[BaseModel], func_kwargs: dict):
    request_headers = dict(request.headers)
    header_dict = {}
    model_properties = header.model_json_schema().get("properties", {})
    for model_field_key, model_field_value in header.model_fields.items():
        key_title = model_field_key.replace("_", "-").title()
        model_field_schema = model_properties.get(model_field_value.alias or model_field_key)
        if model_field_value.alias and header.model_config.get("populate_by_name"):
            key = model_field_value.alias
            key_alias_title = model_field_value.alias.replace("_", "-").title()
            value = request_headers.get(key_alias_title) or request_headers.get(key_title)
        elif model_field_value.alias:
            key = model_field_value.alias
            key_alias_title = model_field_value.alias.replace("_", "-").title()
            value = request_headers.get(key_alias_title)
        else:
            key = model_field_key
            value = request_headers[key_title]
        if value is not None:
            header_dict[key] = value
        if model_field_schema.get("type") == "null":
            header_dict[key] = value  # type:ignore
    # extra keys
    for key, value in request_headers.items():
        if key not in header_dict.keys():
            header_dict[key] = value
    func_kwargs["header"] = header.model_validate(obj=header_dict)


def _validate_cookie(cookie: Type[BaseModel], func_kwargs: dict):
    request_cookies = dict(request.cookies)
    func_kwargs["cookie"] = cookie.model_validate(obj=request_cookies)


def _validate_path(path: Type[BaseModel], path_kwargs: dict, func_kwargs: dict):
    path_obj = path.model_validate(obj=path_kwargs)
    func_kwargs["path"] = path_obj
    # Consume path parameters to prevent from being passed to the function
    for field_name, _ in path_obj:
        path_kwargs.pop(field_name, None)


def _validate_query(query: Type[BaseModel], func_kwargs: dict):
    request_args = request.args
    query_dict = {}
    model_properties = query.model_json_schema().get("properties", {})
    for model_field_key, model_field_value in query.model_fields.items():
        model_field_schema = model_properties.get(model_field_value.alias or model_field_key)
        if model_field_schema.get("type") == "array":
            key, value = _get_list_value(query, request_args, model_field_key, model_field_value)
        # To handle Optional[list]
        elif any(m.get("type") == "array" for m in model_field_schema.get("anyOf", [])):
            key, value = _get_list_value(query, request_args, model_field_key, model_field_value)
        else:
            key, value = _get_value(query, request_args, model_field_key, model_field_value)
        if value is not None and value != []:
            query_dict[key] = value
        if model_field_schema.get("type") == "null":
            query_dict[key] = value
    # extra keys
    for key, value in request_args.items():
        if key not in query_dict.keys():
            query_dict[key] = value
    func_kwargs["query"] = query.model_validate(obj=query_dict)


def _validate_form(form: Type[BaseModel], func_kwargs: dict):
    request_form = request.form
    request_files = request.files
    form_dict = {}
    model_properties = form.model_json_schema().get("properties", {})
    for model_field_key, model_field_value in form.model_fields.items():
        model_field_schema = model_properties.get(model_field_value.alias or model_field_key)
        if model_field_schema.get("type") == "array":
            if model_field_schema.get("items") == {"format": "binary", "type": "string"}:
                # list[FileStorage]
                key, value = _get_list_value(form, request_files, model_field_key, model_field_value)
            else:
                value = []
                key, value_list = _get_list_value(form, request_form, model_field_key, model_field_value)
                for _value in value_list:
                    try:
                        value.append(json.loads(_value))
                    except (JSONDecodeError, TypeError):
                        value.append(_value)
        elif model_field_schema.get("type") == "string" and model_field_schema.get("format") == "binary":
            # FileStorage
            key, value = _get_value(form, request_files, model_field_key, model_field_value)
        else:
            key, _value = _get_value(form, request_form, model_field_key, model_field_value)
            try:
                value = json.loads(_value)
            except (JSONDecodeError, TypeError):
                value = _value
        if value is not None and value != []:
            form_dict[key] = value
        if model_field_schema.get("type") == "null":
            form_dict[key] = value
    # extra keys
    for key, value in {**dict(request_form), **dict(request_files)}.items():
        if key not in form_dict.keys():
            form_dict[key] = value
    func_kwargs["form"] = form.model_validate(obj=form_dict)


def _validate_body(body: Type[BaseModel], func_kwargs: dict):
    obj = request.get_json(silent=True)
    if isinstance(obj, str):
        body_model = body.model_validate_json(json_data=obj)
    else:
        body_model = body.model_validate(obj=obj)
    func_kwargs["body"] = body_model


def _validate_request(
    header: Type[BaseModel] | None = None,
    cookie: Type[BaseModel] | None = None,
    path: Type[BaseModel] | None = None,
    query: Type[BaseModel] | None = None,
    form: Type[BaseModel] | None = None,
    body: Type[BaseModel] | None = None,
    raw: Type[BaseModel] | None = None,
    path_kwargs: dict[Any, Any] | None = None,
) -> dict:
    """
    Validate requests and responses.

    Args:
        header: Header model.
        cookie: Cookie model.
        path: Path model.
        query: Query model.
        form: Form model.
        body: Body model.
        path_kwargs: Path parameters.

    Returns:
        dict: Request kwargs.

    Raises:
        ValidationError: If validation fails.
    """

    # Dictionary to store func kwargs
    func_kwargs: dict = {}

    try:
        # Validate header, cookie, path, and query parameters
        if header:
            _validate_header(header, func_kwargs)
        if cookie:
            _validate_cookie(cookie, func_kwargs)
        if path:
            _validate_path(path, path_kwargs or {}, func_kwargs)
        if query:
            _validate_query(query, func_kwargs)
        if form:
            _validate_form(form, func_kwargs)
        if body:
            _validate_body(body, func_kwargs)
        if raw:
            func_kwargs["raw"] = request
    except ValidationError as e:
        # Create a response with validation error details
        validation_error_callback = getattr(current_app, "validation_error_callback")
        abort(validation_error_callback(e))

    return func_kwargs


def validate_request():
    """
    Decorator to validate the annotated parts of the function and throw and error if applicable.
    """

    def decorator(func):
        setattr(func, "__delay_validate_request__", True)

        is_coroutine_function = inspect.iscoroutinefunction(func)

        if is_coroutine_function:

            @wraps(func)
            async def wrapper(*args, **kwargs):
                header, cookie, path, query, form, body, raw = parse_parameters(func)
                func_kwargs = _validate_request(header, cookie, path, query, form, body, raw, path_kwargs=kwargs)
                # Update func_kwargs with any additional keyword arguments passed from other decorators or calls.
                func_kwargs.update(kwargs)

                return await func(*args, **func_kwargs)

            return wrapper
        else:

            @wraps(func)
            def wrapper(*args, **kwargs):
                header, cookie, path, query, form, body, raw = parse_parameters(func)
                func_kwargs = _validate_request(header, cookie, path, query, form, body, raw, path_kwargs=kwargs)
                # Update func_kwargs with any additional keyword arguments passed from other decorators or calls.
                func_kwargs.update(kwargs)
                return func(*args, **func_kwargs)

            return wrapper

    return decorator

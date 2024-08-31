# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/1 16:54
import json
from json import JSONDecodeError
from typing import Any, Type, Optional, Dict, get_origin, get_args

from flask import request, current_app, abort
from pydantic import ValidationError, BaseModel

from .models import FileStorage


def _validate_header(header: Type[BaseModel], func_kwargs):
    request_headers = dict(request.headers)
    for key, value in header.model_fields.items():
        key_title = key.replace("_", "-").title()
        # Add original key
        if key_title in request_headers.keys():
            if value.alias:
                request_headers[value.alias] = request_headers[key] = request_headers[key_title]
            else:
                request_headers[key] = request_headers[key_title]
    func_kwargs["header"] = header.model_validate(obj=request_headers)


def _validate_cookie(cookie: Type[BaseModel], func_kwargs):
    request_cookies = dict(request.cookies)
    func_kwargs["cookie"] = cookie.model_validate(obj=request_cookies)


def _validate_path(path: Type[BaseModel], path_kwargs, func_kwargs):
    func_kwargs["path"] = path.model_validate(obj=path_kwargs)


def _validate_query(query: Type[BaseModel], func_kwargs):
    request_args = request.args
    query_dict = {}
    for k, v in query.model_fields.items():
        if get_origin(v.annotation) is list:
            value = request_args.getlist(v.alias or k) or request_args.getlist(k)
        else:
            value = request_args.get(v.alias or k) or request_args.get(k)  # type:ignore
        if value is not None:
            query_dict[k] = value
    func_kwargs["query"] = query.model_validate(obj=query_dict)


def _validate_form(form: Type[BaseModel], func_kwargs):
    request_form = request.form
    request_files = request.files
    form_dict = {}
    for k, v in form.model_fields.items():
        if get_origin(v.annotation) is list:
            if get_args(v.annotation)[0] is FileStorage:
                value = request_files.getlist(v.alias or k) or request_files.getlist(k)
            else:
                value = []
                for i in request_form.getlist(v.alias or k) or request_form.getlist(k):
                    try:
                        value.append(json.loads(i))
                    except (JSONDecodeError, TypeError):
                        value.append(i)  # type:ignore
        elif v.annotation is FileStorage:
            value = request_files.get(v.alias or k) or request_files.get(k)  # type:ignore
        else:
            _value = request_form.get(v.alias or k) or request_form.get(k)
            try:
                value = json.loads(_value)  # type:ignore
            except (JSONDecodeError, TypeError):
                value = _value  # type:ignore
        if value is not None:
            form_dict[k] = value
    func_kwargs["form"] = form.model_validate(obj=form_dict)


def _validate_body(body: Type[BaseModel], func_kwargs):
    obj = request.get_json(silent=True)
    if isinstance(obj, str):
        body_model = body.model_validate_json(json_data=obj)
    else:
        body_model = body.model_validate(obj=obj)
    func_kwargs["body"] = body_model


def _validate_request(
        header: Optional[Type[BaseModel]] = None,
        cookie: Optional[Type[BaseModel]] = None,
        path: Optional[Type[BaseModel]] = None,
        query: Optional[Type[BaseModel]] = None,
        form: Optional[Type[BaseModel]] = None,
        body: Optional[Type[BaseModel]] = None,
        raw: Optional[Type[BaseModel]] = None,
        path_kwargs: Optional[Dict[Any, Any]] = None
) -> Dict:
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
        Dict: Request kwargs.

    Raises:
        ValidationError: If validation fails.
    """

    # Dictionary to store func kwargs
    func_kwargs: Dict = {}

    try:
        # Validate header, cookie, path, and query parameters
        if header:
            _validate_header(header, func_kwargs)
        if cookie:
            _validate_cookie(cookie, func_kwargs)
        if path:
            _validate_path(path, path_kwargs, func_kwargs)
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

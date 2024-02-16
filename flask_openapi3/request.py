# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/1 16:54
import json
from json import JSONDecodeError
from typing import Any, Type, Optional, Dict, Union

from flask import request, current_app, abort
from pydantic import ValidationError, BaseModel


def _validate_header(header: Type[BaseModel], func_kwargs):
    request_headers = dict(request.headers) or {}
    for key, value in header.model_json_schema().get("properties", {}).items():
        key_title = key.replace("_", "-").title()
        # Add original key
        if key_title in request_headers.keys():
            request_headers[key] = request_headers[key_title]
    func_kwargs.update({"header": header.model_validate(obj=request_headers)})


def _validate_cookie(cookie: Type[BaseModel], func_kwargs):
    request_cookies = dict(request.cookies) or {}
    func_kwargs.update({"cookie": cookie.model_validate(obj=request_cookies)})


def _validate_path(path: Type[BaseModel], path_kwargs, func_kwargs):
    func_kwargs.update({"path": path.model_validate(obj=path_kwargs)})


def _validate_query(query: Type[BaseModel], func_kwargs):
    request_args = request.args
    query_dict = {}
    for k, v in query.model_json_schema().get("properties", {}).items():
        value: Union[list, Optional[str]]
        if v.get("type") == "array":
            value = request_args.getlist(k)
        else:
            value = request_args.get(k)
        if value is not None:
            query_dict[k] = value
    func_kwargs.update({"query": query.model_validate(obj=query_dict)})


def _validate_form(form: Type[BaseModel], func_kwargs):
    request_form = request.form
    request_files = request.files
    form_dict = {}
    for k, v in form.model_json_schema().get("properties", {}).items():
        if v.get("type") == "array":
            items = v.get("items", {})
            if items.get("type") == "string" and items.get("format") == "binary":
                # List[FileStorage]
                value = request_files.getlist(k)
            elif items.get("type") in ["object", "null", None]:
                # list object, None, $ref, anyOf
                value = []
                for i in request_form.getlist(k):
                    try:
                        json_loads_result = json.loads(i)
                    except JSONDecodeError:
                        json_loads_result = i
                    value.append(json_loads_result)
            else:
                # List[str], List[int] ...
                value = request_form.getlist(k)  # type:ignore
        elif v.get("type") in ["object", "null", None]:
            # list object, None, $ref, anyOf
            try:
                value = json.loads(request_form.get(k)) if request_form.get(k) else None  # type:ignore
            except JSONDecodeError:
                value = request_form.get(k)  # type:ignore
        else:
            if v.get("format") == "binary":
                # FileStorage
                value = request_files.get(k)  # type:ignore
            else:
                # str, int ...
                value = request_form.get(k)  # type:ignore
        if value is not None:
            form_dict[k] = value
    func_kwargs.update({"form": form.model_validate(obj=form_dict)})


def _validate_body(body: Type[BaseModel], func_kwargs):
    obj = request.get_json(silent=True) or {}
    if isinstance(obj, str):
        body_model = body.model_validate_json(json_data=obj)
    else:
        body_model = body.model_validate(obj=obj)
    func_kwargs.update({"body": body_model})


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
        Union[Response, Dict]: Request kwargs.

    Raises:
        ValidationError: If validation fails.
    """

    # Dictionary to store func kwargs
    func_kwargs: Dict = dict()

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
            func_kwargs.update({"raw": request})
    except ValidationError as e:
        # Create a response with validation error details
        validation_error_callback = getattr(current_app, "validation_error_callback")
        abort(validation_error_callback(e))

    return func_kwargs

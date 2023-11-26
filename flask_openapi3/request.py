# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/1 16:54
import json
from json import JSONDecodeError
from typing import Any, Type, Optional, Dict

from flask import request, current_app, abort
from pydantic import ValidationError, BaseModel
from pydantic.error_wrappers import ErrorWrapper


def _validate_header(header, func_kwargs):
    request_headers = dict(request.headers) or {}
    for key, value in header.schema().get("properties", {}).items():
        key_title = key.replace("_", "-").title()
        # Add original key
        if key_title in request_headers.keys():
            request_headers[key] = request_headers[key_title]
    func_kwargs.update({"header": header(**request_headers)})


def _validate_cookie(cookie, func_kwargs):
    request_cookies = cookie(**request.cookies or {})
    func_kwargs.update({"cookie": request_cookies})


def _validate_path(path, path_kwargs, func_kwargs):
    request_path = path(**path_kwargs)
    func_kwargs.update({"path": request_path})


def _validate_query(query, func_kwargs):
    request_args = request.args
    query_dict = {}
    for k, v in query.schema().get("properties", {}).items():
        if v.get("type") == "array":
            value = request_args.getlist(k)
        else:
            value = request_args.get(k)
        if value is not None:
            query_dict[k] = value
    func_kwargs.update({"query": query(**query_dict)})


def _validate_form(form, func_kwargs):
    request_form = request.form
    request_files = request.files
    form_dict = {}
    for k, v in form.schema().get("properties", {}).items():
        if v.get("type") == "array":
            items = v.get("items", {})
            if items.get("type") == "string" and items.get("format") == "binary":
                # List[FileStorage]
                # eg: {"title": "Files", "type": "array", "items": {"format": "binary", "type": "string"}
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
                # eg: {"title": "Files", "type": "array", "items": {"type": "string"}
                value = request_form.getlist(k)
        elif v.get("type") in ["object", "null", None]:
            # list object, None, $ref, anyOf
            try:
                value = json.loads(request_form.get(k)) if request_form.get(k) else None
            except JSONDecodeError:
                value = request_form.get(k)
        else:
            if v.get("format") == "binary":
                # FileStorage
                value = request_files.get(k)
            else:
                # str, int ...
                value = request_form.get(k)
        if value is not None:
            form_dict[k] = value
    func_kwargs.update({"form": form(**form_dict)})


def _validate_body(body, func_kwargs):
    obj = request.get_json(silent=True) or {}
    if isinstance(obj, str):
        try:
            obj = json.loads(obj)
        except JSONDecodeError as e:
            raise ValidationError([ErrorWrapper(e, loc="__root__")], body)
    if body.__custom_root_type__:
        # https://docs.pydantic.dev/latest/usage/models/#custom-root-types
        body_ = body(__root__=obj)
    else:
        body_ = body(**obj)
    func_kwargs.update({"body": body_})


def _validate_request(
        header: Optional[Type[BaseModel]] = None,
        cookie: Optional[Type[BaseModel]] = None,
        path: Optional[Type[BaseModel]] = None,
        query: Optional[Type[BaseModel]] = None,
        form: Optional[Type[BaseModel]] = None,
        body: Optional[Type[BaseModel]] = None,
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
    except ValidationError as e:
        # Create a response with validation error details
        validation_error_callback = getattr(current_app, "validation_error_callback")
        abort(validation_error_callback(e))

    return func_kwargs

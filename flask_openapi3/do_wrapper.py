# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/1 16:54
import json
from json import JSONDecodeError
from typing import Any, Type, Callable

from flask import request, make_response
from flask.wrappers import Response
from pydantic import ValidationError, BaseModel
from pydantic.error_wrappers import ErrorWrapper


def _do_header(header, request_kwargs):
    request_headers = dict(request.headers) or {}
    for key, value in header.__annotations__.items():
        key_title = key.title()
        # add original key
        if key_title in request_headers.keys():
            request_headers[key] = request_headers[key_title]
    request_kwargs.update({"header": header(**request_headers)})


def _do_cookie(cookie, request_kwargs):
    request_cookies = cookie(**request.cookies or {})
    request_kwargs.update({"cookie": request_cookies})


def _do_path(path, kwargs, request_kwargs):
    request_path = path(**kwargs)
    request_kwargs.update({"path": request_path})


def _do_query(query, request_kwargs):
    request_args = request.args
    query_dict = {}
    for k, v in query.schema().get('properties', {}).items():
        if v.get('type') == 'array':
            value = request_args.getlist(k)
        else:
            value = request_args.get(k)
        if value is not None:
            query_dict[k] = value
    request_kwargs.update({"query": query(**query_dict)})


def _do_form(form, request_kwargs):
    request_form = request.form
    request_files = request.files
    form_dict = {}
    for k, v in form.schema().get('properties', {}).items():
        if v.get('type') == 'array':
            items = v.get('items', {})
            if items.get('type') == 'string' and items.get('format') == 'binary':
                # List[FileStorage]
                # {'title': 'Files', 'type': 'array', 'items': {'format': 'binary', 'type': 'string'}
                value = request_files.getlist(k)
            else:
                # List[str], List[int] ...
                # {'title': 'Files', 'type': 'array', 'items': {'type': 'string'}
                value = request_form.getlist(k)
        else:
            if v.get('format') == 'binary':
                # FileStorage
                value = request_files.get(k)
            else:
                # str, int ...
                value = request_form.get(k)
        if value is not None:
            form_dict[k] = value
    request_kwargs.update({"form": form(**form_dict)})


def _do_body(body, request_kwargs):
    obj = request.get_json(silent=True) or {}
    if isinstance(obj, str):
        try:
            obj = json.loads(obj)
        except JSONDecodeError as e:
            raise ValidationError([ErrorWrapper(e, loc='__root__')], body)
    if body.__custom_root_type__:
        # https://pydantic-docs.helpmanual.io/usage/models/#custom-root-types
        body_ = body(__root__=obj)
    else:
        body_ = body(**obj)
    request_kwargs.update({"body": body_})


def _do_wrapper(
        func: Callable,
        *,
        header: Type[BaseModel] = None,
        cookie: Type[BaseModel] = None,
        path: Type[BaseModel] = None,
        query: Type[BaseModel] = None,
        form: Type[BaseModel] = None,
        body: Type[BaseModel] = None,
        **kwargs: Any
) -> Response:
    """
    Validate requests and responses
    :param func: view func
    :param responses: response model
    :param header: header model
    :param cookie: cookie model
    :param path: path model
    :param query: query model
    :param form: form model
    :param body: body model
    :param kwargs: path parameters
    :return:
    """
    # validate header, cookie, path and query
    request_kwargs = dict()
    try:
        if header:
            _do_header(header, request_kwargs)
        if cookie:
            _do_cookie(cookie, request_kwargs)
        if path:
            _do_path(path, kwargs, request_kwargs)
        if query:
            _do_query(query, request_kwargs)
        if form:
            _do_form(form, request_kwargs)
        if body:
            _do_body(body, request_kwargs)
    except ValidationError as e:
        response = make_response(e.json())
        response.headers['Content-Type'] = 'application/json'
        response.status_code = 422
        return response

    # handle request
    response = func(**request_kwargs)

    return response

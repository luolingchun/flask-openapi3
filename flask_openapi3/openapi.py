# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:25
import os
from functools import wraps
from typing import Optional, List, Dict, Union

from flask import Flask, Blueprint, render_template, request
from pydantic import ValidationError, BaseModel

from flask_openapi3.models import Info, APISpec, Tag, PathItem, Components
from flask_openapi3.models.common import Reference
from flask_openapi3.models.path import RequestBody
from flask_openapi3.models.security import SecurityScheme
from flask_openapi3.utils import _parse_rule, get_func_parameters, parse_path, parse_query, get_operation, \
    get_responses, parse_header, parse_cookie, parse_form, parse_json


def _do_wrapper(func, responses, header, cookie, path, query, form, json, validate_resp, **kwargs):
    if responses is None:
        responses = {}
    assert isinstance(responses, dict), "invalid `dict`"
    # validate header, cookie, path and query
    kwargs_ = dict()
    try:
        if header:
            header_ = header.annotation(**request.headers)
            kwargs_.update({"header": header_})
        if cookie:
            cookie_ = cookie.annotation(**request.cookies)
            kwargs_.update({"cookie": cookie_})
        if path:
            path_ = path.annotation(**kwargs)
            kwargs_.update({"path": path_})
        if query:
            query_ = query.annotation(**request.args)
            kwargs_.update({"query": query_})
        if form:
            form_ = form.annotation(**request.form)
            kwargs_.update({"form": form_})
        if json:
            json_ = json.annotation(**request.get_json(silent=True))
            kwargs_.update({"json": json_})
    except ValidationError as e:
        return e.json(), 422
    # validate response(only validate 200)
    resp = func(**kwargs_)
    if validate_resp:
        for key, response in responses.items():
            if key != "200":
                continue
            assert issubclass(response, BaseModel), "invalid `pedantic.BaseModel`"
            try:
                _resp = resp
                if isinstance(resp, tuple):  # noqa
                    _resp = resp[0]
                response(**_resp)
            except ValidationError as e:
                return e.json(), 500

    return resp


class OpenAPI(Flask):
    def __init__(self, import_name, info, securitySchemes: Optional[Dict[str, Union[SecurityScheme, Reference]]] = None,
                 **kwargs):
        super(OpenAPI, self).__init__(import_name, **kwargs)

        self.openapi_version = "3.0.3"

        assert isinstance(info, Info), f"Info is required (got type {type(info)})"
        self.info = info
        self.securitySchemes = securitySchemes
        self.paths = dict()
        self.components_schemas = dict()
        self.components = Components()
        self.tags = []
        self.tag_names = []
        self.api_name = 'openapi'
        self.api_doc_url = f"/{self.api_name}.json"

        self.init_doc()

    def init_doc(self):
        _here = os.path.dirname(__file__)
        template_folder = os.path.join(_here, 'templates')
        static_folder = os.path.join(template_folder, 'static')

        blueprint = Blueprint(
            self.api_name,
            __name__,
            url_prefix=f'/{self.api_name}',
            template_folder=template_folder,
            static_folder=static_folder
        )
        blueprint.add_url_rule(rule=self.api_doc_url, endpoint=self.api_name, view_func=lambda: self.api_doc)
        blueprint.add_url_rule(rule='/redoc', endpoint='redoc',
                               view_func=lambda: render_template("redoc.html", api_doc_url=f'{self.api_name}.json'))
        blueprint.add_url_rule(rule='/swagger', endpoint='swagger',
                               view_func=lambda: render_template("swagger.html", api_doc_url=f'{self.api_name}.json'))
        blueprint.add_url_rule(rule='/', endpoint='index',
                               view_func=lambda: render_template("index.html"))
        self.register_blueprint(blueprint)

    @property
    def api_doc(self):
        spec = APISpec(openapi=self.openapi_version, info=self.info)
        spec.tags = self.tags
        spec.paths = self.paths
        self.components.schemas = self.components_schemas
        self.components.securitySchemes = self.securitySchemes
        spec.components = self.components
        return spec.dict(by_alias=True, exclude_none=True)

    def _do_decorator(self, rule, func, tags, responses, security, method='get'):
        if responses is None:
            responses = {}
        assert isinstance(responses, dict), "invalid `dict`"
        # store tags
        for tag in tags:
            if tag.name not in self.tag_names:
                self.tag_names.append(tag.name)
                self.tags.extend(tags)
        operation = get_operation(func)
        operation.tags = *[tag.name for tag in tags],
        # start parse parameters
        parameters = []
        header = get_func_parameters(func, 'header')
        cookie = get_func_parameters(func, 'cookie')
        path = get_func_parameters(func, 'path')
        query = get_func_parameters(func, 'query')
        form = get_func_parameters(func, 'form')
        json = get_func_parameters(func, 'json')
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
            _parameters, components_schemas = parse_query(query)
            parameters.extend(_parameters)
            self.components_schemas.update(**components_schemas)
        if form:
            content, components_schemas = parse_form(form)
            self.components_schemas.update(**components_schemas)
            requestBody = RequestBody(**{
                "content": content,
            })
            operation.requestBody = requestBody
        if json:
            content, components_schemas = parse_json(json)
            self.components_schemas.update(**components_schemas)
            requestBody = RequestBody(**{
                "content": content,
            })
            operation.requestBody = requestBody
        operation.parameters = parameters
        # end parse parameters
        # start parse response
        _responses, _schemas = get_responses(responses)
        operation.responses = _responses
        self.components_schemas.update(**_schemas)
        # end parse response
        # add security
        operation.security = security
        uri = _parse_rule(rule)
        if method == 'get':
            self.paths[uri] = PathItem(get=operation)
        elif method == 'post':
            self.paths[uri] = PathItem(post=operation)
        elif method == 'put':
            self.paths[uri] = PathItem(put=operation)
        elif method == 'patch':
            self.paths[uri] = PathItem(patch=operation)
        elif method == 'delete':
            self.paths[uri] = PathItem(delete=operation)

        return header, cookie, path, query, form, json

    def get(self, rule, tags: Optional[List[Tag]] = None, responses=None, validate_resp=True, security=None):
        def decorator(func):
            header, cookie, path, query, form, json = self._do_decorator(rule, func, tags, responses, security)

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, json, validate_resp, **kwargs)
                return resp

            options = {"methods": ["GET"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def post(self, rule, tags: Optional[List[Tag]] = None, responses=None, validate_resp=True, security=None):
        def decorator(func):
            header, cookie, path, query, form, json = self._do_decorator(rule, func, tags, responses, security, "post")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, json, validate_resp, **kwargs)
                return resp

            options = {"methods": ["POST"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def put(self, rule, tags: Optional[List[Tag]] = None, responses=None, validate_resp=True, security=None):
        def decorator(func):
            header, cookie, path, query, form, json = self._do_decorator(rule, func, tags, responses, security, "put")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, json, validate_resp, **kwargs)
                return resp

            options = {"methods": ["PUT"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def delete(self, rule, tags: Optional[List[Tag]] = None, responses=None, validate_resp=True, security=None):
        def decorator(func):
            header, cookie, path, query, form, json = self._do_decorator(rule, func, tags, responses, security,
                                                                         "delete")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, json, validate_resp, **kwargs)
                return resp

            options = {"methods": ["DELETE"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def patch(self, rule, tags: Optional[List[Tag]] = None, responses=None, validate_resp=True, security=None):
        def decorator(func):
            header, cookie, path, query, form, json = self._do_decorator(rule, func, tags, responses, security, "patch")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, json, validate_resp, **kwargs)
                return resp

            options = {"methods": ["PATCH"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:25
import os
from functools import wraps
from typing import Optional, List, Dict, Union

from flask import Flask, Blueprint, render_template, request
from pydantic import ValidationError

from flask_openapi3.models import Info, APISpec, Tag, PathItem, Components
from flask_openapi3.models.common import Reference
from flask_openapi3.models.security import SecurityScheme
from flask_openapi3.utils import _parse_rule, get_func_parameters, parse_path, parse_query, get_operation, get_responses


class OpenAPI(Flask):
    def __init__(self, import_name, info, securitySchemes: Optional[Dict[str, Union[SecurityScheme, Reference]]] = None,
                 **kwargs):
        super(OpenAPI, self).__init__(import_name, **kwargs)
        self.openapi_version = "3.0.3"

        if not isinstance(info, Info):
            raise TypeError(f"Info is required (got type {type(info)})")
        self.info = info
        self.securitySchemes = securitySchemes
        self.paths = dict()
        self.schemas = dict()
        self.components = Components()
        self.tags = []
        self.name = 'openapi'
        self.api_doc_url = f"/{self.name}.json"

        self.init_app()

    def init_app(self):
        _here = os.path.dirname(__file__)
        template_folder = os.path.join(_here, 'templates')
        static_folder = os.path.join(template_folder, 'static')

        blueprint = Blueprint(
            self.name,
            __name__,
            url_prefix=f'/{self.name}',
            template_folder=template_folder,
            static_folder=static_folder
        )
        blueprint.add_url_rule(rule=self.api_doc_url, endpoint=self.name, view_func=lambda: self.api_doc)
        blueprint.add_url_rule(rule='/redoc', endpoint='redoc',
                               view_func=lambda: render_template("redoc.html", api_doc_url=f'{self.name}.json'))
        blueprint.add_url_rule(rule='/swagger', endpoint='swagger',
                               view_func=lambda: render_template("swagger.html", api_doc_url=f'{self.name}.json'))
        blueprint.add_url_rule(rule='/', endpoint='index',
                               view_func=lambda: render_template("index.html", api_doc_url=f'{self.name}.json'))
        self.register_blueprint(blueprint)

    @property
    def api_doc(self):
        spec = APISpec(openapi=self.openapi_version, info=self.info)
        spec.tags = self.tags
        spec.paths = self.paths
        self.components.schemas = self.schemas
        self.components.securitySchemes = self.securitySchemes
        spec.components = self.components
        return spec.dict(by_alias=True, exclude_none=True)

    #
    # def get_paths(self):
    #     paths = {}
    #     for rule in current_app.url_map.iter_rules():
    #         if any(str(rule).startswith(path) for path in (f"/{self.name}", "/static")):
    #             continue
    #         print(str(rule))
    #         print(rule.methods)
    #         uri, parameters = _parse_rule(rule)
    #         path_item = PathItem(get=Operation(parameters=parameters))
    #         paths[uri] = path_item
    #     return paths
    #
    # def validate(self):
    #     pass

    def get(self, rule, tags: Optional[List[Tag]] = None, response=None, security=None):
        # store tags
        self.tags.extend(tags)

        def decorator(func):
            operation = get_operation(func, tags)
            # start parse parameters
            parameters = []
            path = get_func_parameters(func, 'path')
            query = get_func_parameters(func, 'query')
            if path:
                # get args from route path
                _parameters = parse_path(path)
                parameters.extend(_parameters)
            if query:
                # get args from route query
                _parameters, _schemas = parse_query(query)
                parameters.extend(_parameters)
                self.schemas.update(**_schemas)
            operation.parameters = parameters
            # end parse parameters
            # start parse response
            responses, _schemas = get_responses(response)
            operation.responses = responses
            self.schemas.update(**_schemas)
            # end parse response
            # add security
            operation.security = security
            uri = _parse_rule(rule)
            self.paths[uri] = PathItem(get=operation)

            @wraps(func)
            def wrapper(**kwargs):
                # validate path and query
                kwargs_ = dict()
                try:
                    if path:
                        path_ = path.annotation(**kwargs)
                        kwargs_.update({"path": path_})
                    if query:
                        query_ = query.annotation(**request.args)
                        kwargs_.update({"query": query_})
                except ValidationError as e:
                    return e.json(), 422
                # validate response
                resp = func(**kwargs_)
                if response:
                    try:
                        if isinstance(resp, tuple):
                            resp = resp[0]
                        response(**resp)
                    except ValidationError as e:
                        return e.json(), 500

                return func(**kwargs_)

            options = {"methods": ["GET"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def post(self, path):
        def decorator(func, **options):
            endpoint = options.pop("endpoint", None)
            options['methods'] = ['POST']
            self.add_url_rule(path, endpoint, func, **options)
            return func

        return decorator

    def put(self, path):
        def decorator(func, **options):
            endpoint = options.pop("endpoint", None)
            options['methods'] = ['PUT']
            self.add_url_rule(path, endpoint, func, **options)
            return func

        return decorator

    def delete(self, path):
        def decorator(func, **options):
            endpoint = options.pop("endpoint", None)
            options['methods'] = ['DELETE']
            self.add_url_rule(path, endpoint, func, **options)
            return func

        return decorator

    def patch(self, path):
        def decorator(func, **options):
            endpoint = options.pop("endpoint", None)
            options['methods'] = ['PATCH']
            self.add_url_rule(path, endpoint, func, **options)
            return func

        return decorator

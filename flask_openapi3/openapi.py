# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:25
import inspect
import os
from functools import wraps
from typing import Optional, List

from flask import Flask, Blueprint, render_template, request
from pydantic import ValidationError

from flask_openapi3.models import Info, APISpec, Tag, PathItem, Components
from flask_openapi3.models.path import Operation
from flask_openapi3.utils import _parse_rule, get_func_parameters, _parse_path, _parse_query


class OpenAPI(Flask):
    def __init__(self, import_name, info, **kwargs):
        super(OpenAPI, self).__init__(import_name, **kwargs)
        self.openapi_version = "3.0.3"

        if not isinstance(info, Info):
            raise TypeError(f"Info is required (got type {type(info)})")
        self.info = info
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
        spec.components = self.components
        return spec.dict(by_alias=True, exclude_unset=True)

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

    def get(self, rule, *, tags: Optional[List[Tag]] = None):
        self.tags.extend(tags)

        def decorator(func):

            doc = inspect.getdoc(func) or ''
            uri = _parse_rule(rule)
            get = Operation(
                tags=[tag.name for tag in tags],
                summary=doc.split('\n')[0],
                description=doc.split('\n')[-1]
            )

            func_parameters = get_func_parameters(func)
            parameters = []
            path = func_parameters.get('path')
            query = func_parameters.get('query')
            if path:
                _parameters = _parse_path(path)
                parameters.extend(_parameters)
            if query:
                _parameters, _schema = _parse_query(query)
                parameters.extend(_parameters)
                self.schemas.update(**_schema)

            get.parameters = parameters
            get.responses = {"500": "error"}
            self.paths[uri] = PathItem(get=get)

            @wraps(func)
            def wrapper(**kwargs):
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

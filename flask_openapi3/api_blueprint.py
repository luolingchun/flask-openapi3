# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/1 16:54
import re
from copy import deepcopy
from functools import wraps
from typing import Optional, List, Dict, Any, Type, Callable, Tuple

from flask import Blueprint
from flask.wrappers import Response
from pydantic import BaseModel

from .do_wrapper import _do_wrapper
from .http import HTTPMethod
from .models import Tag, Components
from .types import OpenAPIResponsesType
from .utils import get_operation, get_responses, parse_and_store_tags, parse_parameters, validate_responses_type, \
    parse_method, get_operation_id_for_path


class APIBlueprint(Blueprint):
    def __init__(
            self,
            name: str,
            import_name: str,
            *,
            abp_tags: Optional[List[Tag]] = None,
            abp_security: Optional[List[Dict[str, List[str]]]] = None,
            abp_responses: OpenAPIResponsesType = None,
            doc_ui: bool = True,
            **kwargs: Any
    ) -> None:
        """
        Based on Flask Blueprint

        Arguments:
            name: The name of the blueprint. Will be prepended to each endpoint name.
            import_name: The name of the blueprint package, usually
                         ``__name__``. This helps locate the ``root_path`` for the blueprint.
            abp_tags: APIBlueprint tags for every api
            abp_security: APIBlueprint security for every api
            abp_responses: APIBlueprint response model
            doc_ui: add openapi document UI(swagger and redoc). Defaults to True.
            kwargs: Flask Blueprint kwargs
        """
        super(APIBlueprint, self).__init__(name, import_name, **kwargs)
        self.paths = dict()
        self.components_schemas = dict()
        self.components = Components()
        self.tags = []
        self.tag_names = []

        self.abp_tags = abp_tags or []
        self.abp_security = abp_security or []
        self.abp_responses = abp_responses or {}
        self.doc_ui = doc_ui

    def register_api(self, api: "APIBlueprint") -> None:
        """Register a nested APIBlueprint"""
        if api is self:
            raise ValueError("Cannot register a api blueprint on itself")

        for tag in api.tags:
            if tag.name not in self.tag_names:
                self.tags.append(tag)

        for path_url, path_item in api.paths.items():
            trail_slash = path_url.endswith("/")
            # merge url_prefix and new api blueprint path url
            uri = self.url_prefix.rstrip("/") + "/" + path_url.lstrip("/") if self.url_prefix else path_url
            # strip the right slash
            if not trail_slash:
                uri = uri.rstrip("/")
            self.paths[uri] = path_item

        self.components_schemas.update(**api.components_schemas)

        self.register_blueprint(api)

    def _do_decorator(
            self,
            rule: str,
            func: Callable,
            *,
            tags: List[Tag] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            extra_responses: Dict[str, dict] = None,
            security: List[Dict[str, List[Any]]] = None,
            deprecated: Optional[bool] = None,
            operation_id: Optional[str] = None,
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> Tuple[
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Dict[str, Type[BaseModel]]
    ]:
        """
        Collect openapi specification information
        :param rule: flask route
        :param func: flask view_func
        :param tags: api tag
        :param responses: response model
        :param extra_responses: extra response dict
        :param security: security name
        :param doc_ui: add openapi document UI(swagger and redoc). Defaults to True.
        :param deprecated: mark as deprecated support. Default to not True.
        :param operation_id: unique string used to identify the operation.
        :param method: api method
        :return:
        """
        if self.doc_ui is True and doc_ui is True:
            if responses is None:
                responses = {}
            if extra_responses is None:
                extra_responses = {}
            validate_responses_type(responses)
            validate_responses_type(self.abp_responses)
            validate_responses_type(extra_responses)
            # global response combine api responses
            combine_responses = deepcopy(self.abp_responses)
            combine_responses.update(**responses)
            # create operation
            operation = get_operation(func, summary=summary, description=description)
            # add security
            if security is None:
                security = []
            operation.security = security + self.abp_security or None
            # only set `deprecated` if True otherwise leave it as None
            if deprecated:
                operation.deprecated = True
            # Unique string used to identify the operation.
            if operation_id:
                operation.operationId = operation_id
            else:
                operation.operationId = get_operation_id_for_path(name=func.__name__, path=rule, method=method)
            # store tags
            tags = tags + self.abp_tags if tags else self.abp_tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)
            # parse parameters
            header, cookie, path, query, form, body = \
                parse_parameters(func, components_schemas=self.components_schemas, operation=operation)
            # parse response
            get_responses(combine_responses, extra_responses, self.components_schemas, operation)
            # /pet/<petId> --> /pet/{petId}
            uri = re.sub(r"<([^<:]+:)?", "{", rule).replace(">", "}")
            trail_slash = uri.endswith("/")
            # merge url_prefix and uri
            uri = self.url_prefix.rstrip("/") + "/" + uri.lstrip("/") if self.url_prefix else uri
            if not trail_slash:
                uri = uri.rstrip("/")
            # parse method
            parse_method(uri, method, self.paths, operation)
            return header, cookie, path, query, form, body, combine_responses
        else:
            # parse parameters
            header, cookie, path, query, form, body = parse_parameters(func, doc_ui=False)
            return header, cookie, path, query, form, body, {}

    def get(
            self,
            rule: str,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            responses: OpenAPIResponsesType = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            operation_id: Optional[str] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["GET"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    operation_id=operation_id,
                    doc_ui=doc_ui,
                    method=HTTPMethod.GET
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options.update({"methods": [HTTPMethod.GET]})
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def post(
            self,
            rule: str,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            responses: OpenAPIResponsesType = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            operation_id: Optional[str] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["POST"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    operation_id=operation_id,
                    doc_ui=doc_ui,
                    method=HTTPMethod.POST
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options.update({"methods": [HTTPMethod.POST]})
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def put(
            self,
            rule: str,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            responses: OpenAPIResponsesType = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            operation_id: Optional[str] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["PUT"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    operation_id=operation_id,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PUT
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options.update({"methods": [HTTPMethod.PUT]})
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def delete(
            self,
            rule: str,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            responses: OpenAPIResponsesType = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            operation_id: Optional[str] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["DELETE"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    operation_id=operation_id,
                    doc_ui=doc_ui,
                    method=HTTPMethod.DELETE
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options.update({"methods": [HTTPMethod.DELETE]})
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def patch(
            self,
            rule: str,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            responses: OpenAPIResponsesType = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            operation_id: Optional[str] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["PATCH"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    operation_id=operation_id,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PATCH
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options.update({"methods": [HTTPMethod.PATCH]})
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

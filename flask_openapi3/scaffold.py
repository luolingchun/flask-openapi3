# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/8/30 9:40
from abc import ABC
from functools import wraps
from typing import Callable, List, Optional, Dict, Type, Any, Tuple

from flask.scaffold import Scaffold
from flask.wrappers import Response
from pydantic import BaseModel

from .do_wrapper import _do_wrapper
from .http import HTTPMethod
from .models import ExternalDocumentation, ExtraRequestBody
from .models.server import Server
from .models.tag import Tag


class _Scaffold(Scaffold, ABC):
    def _do_decorator(
            self,
            rule: str,
            func: Callable,
            *,
            tags: List[Tag] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            extra_responses: Dict[str, dict] = None,
            deprecated: Optional[bool] = None,
            security: List[Dict[str, List[Any]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel]]:
        raise NotImplementedError

    def register_api(self, api) -> None:
        raise NotImplementedError

    def get(
            self,
            rule: str,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["GET"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    extra_body=extra_body,
                    responses=responses,
                    extra_responses=extra_responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    doc_ui=doc_ui,
                    method=HTTPMethod.GET
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
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
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["POST"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    extra_body=extra_body,
                    responses=responses,
                    extra_responses=extra_responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    doc_ui=doc_ui,
                    method=HTTPMethod.POST
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
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
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["PUT"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    extra_body=extra_body,
                    responses=responses,
                    extra_responses=extra_responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PUT
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
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
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["DELETE"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    extra_body=extra_body,
                    responses=responses,
                    extra_responses=extra_responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    doc_ui=doc_ui,
                    method=HTTPMethod.DELETE
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
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
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=["PATCH"])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    extra_body=extra_body,
                    responses=responses,
                    extra_responses=extra_responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PATCH
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
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

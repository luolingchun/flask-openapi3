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
from .models import ExternalDocumentation
from .models.common import ExtraRequestBody
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
            extra_form: Optional[ExtraRequestBody] = None,
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
            extra_form: Optional[ExtraRequestBody] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for rest api, like: app.route(methods=["GET"])
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: Extra information describing the request body(application/form).
            extra_body: Extra information describing the request body(application/json).
            responses: Responses model, must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Add openapi document UI(swagger, rapidoc and redoc). Defaults to True.
        """

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
                    extra_form=extra_form,
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
            extra_form: Optional[ExtraRequestBody] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for rest api, like: app.route(methods=["POST"])
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: Extra information describing the request body(application/form).
            extra_body: Extra information describing the request body(application/json).
            responses: Responses model, must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Declares this operation to be show.
        """

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
                    extra_form=extra_form,
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
            extra_form: Optional[ExtraRequestBody] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for rest api, like: app.route(methods=["PUT"])
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: Extra information describing the request body(application/form).
            extra_body: Extra information describing the request body(application/json).
            responses: Responses model, must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Declares this operation to be show.
        """

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
                    extra_form=extra_form,
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
            extra_form: Optional[ExtraRequestBody] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for rest api, like: app.route(methods=["DELETE"])
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: Extra information describing the request body(application/form).
            extra_body: Extra information describing the request body(application/json).
            responses: Responses model, must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Declares this operation to be show.
        """

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
                    extra_form=extra_form,
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
            extra_form: Optional[ExtraRequestBody] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for rest api, like: app.route(methods=["PATCH"])
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: Extra information describing the request body(application/form).
            extra_body: Extra information describing the request body(application/json).
            responses: Responses model, must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Declares this operation to be show.
        """

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
                    extra_form=extra_form,
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

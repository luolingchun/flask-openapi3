# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/8/30 9:40
import functools
import inspect
import sys
from abc import ABC
from functools import wraps
from typing import Callable, List, Optional, Dict, Type, Any, Tuple

from flask.scaffold import Scaffold
from flask.wrappers import Response
from pydantic import BaseModel

from .http import HTTPMethod
from .models import ExternalDocumentation
from .models.common import ExtraRequestBody
from .models.server import Server
from .models.tag import Tag
from .request import _do_request

if sys.version_info >= (3, 8):
    iscoroutinefunction = inspect.iscoroutinefunction
else:
    def iscoroutinefunction(func: Any) -> bool:
        while inspect.ismethod(func):
            func = func.__func__

        while isinstance(func, functools.partial):
            func = func.func

        return inspect.iscoroutinefunction(func)


class APIScaffold(Scaffold, ABC):
    def _do_decorator(
            self,
            rule: str,
            func: Callable,
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
            method: str = HTTPMethod.GET
    ) -> Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel]]:
        raise NotImplementedError

    def register_api(self, api) -> None:
        raise NotImplementedError

    @staticmethod
    def create_view_func(
            func,
            header,
            cookie,
            path,
            query,
            form,
            body,
            view_class=None,
            view_kwargs=None
    ):
        is_coroutine_function = iscoroutinefunction(func)
        if is_coroutine_function:
            @wraps(func)
            async def view_func(**kwargs) -> Response:
                result = _do_request(
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                if isinstance(result, Response):
                    # 422
                    return result
                # handle async request
                if view_class:
                    signature = inspect.signature(view_class.__init__)
                    parameters = signature.parameters
                    if parameters.get("view_kwargs"):
                        view_object = view_class(view_kwargs=view_kwargs)
                    else:
                        view_object = view_class()
                    response = await func(view_object, **result)
                else:
                    response = await func(**result)
                return response
        else:
            @wraps(func)
            def view_func(**kwargs) -> Response:
                result = _do_request(
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                if isinstance(result, Response):
                    # 422
                    return result
                # handle request
                if view_class:
                    signature = inspect.signature(view_class.__init__)
                    parameters = signature.parameters
                    if parameters.get("view_kwargs"):
                        view_object = view_class(view_kwargs=view_kwargs)
                    else:
                        view_object = view_class()
                    response = func(view_object, **result)
                else:
                    response = func(**result)
                return response

        if not hasattr(func, "view"):
            func.view = view_func

        return func.view

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
            responses: response's model must be pydantic BaseModel.
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

            view_func = self.create_view_func(func, header, cookie, path, query, form, body)
            options.update({"methods": [HTTPMethod.GET]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

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
            responses: response's model must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Declares this operation to be shown.
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

            view_func = self.create_view_func(func, header, cookie, path, query, form, body)
            options.update({"methods": [HTTPMethod.POST]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

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
            responses: response's model must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Declares this operation to be shown.
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

            view_func = self.create_view_func(func, header, cookie, path, query, form, body)
            options.update({"methods": [HTTPMethod.PUT]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

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
            responses: response's model must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Declares this operation to be shown.
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

            view_func = self.create_view_func(func, header, cookie, path, query, form, body)
            options.update({"methods": [HTTPMethod.DELETE]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

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
            responses: response's model must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Declares this operation to be shown.
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

            view_func = self.create_view_func(func, header, cookie, path, query, form, body)
            options.update({"methods": [HTTPMethod.PATCH]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

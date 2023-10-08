# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/8/30 9:40
import functools
import inspect
import sys
import warnings
from abc import ABC
from functools import wraps
from typing import Callable, List, Optional, Dict, Any

from flask.scaffold import Scaffold
from flask.wrappers import Response as FlaskResponse

from ._http import HTTPMethod
from .models import ExternalDocumentation
from .models import ExtraRequestBody
from .models import Server
from .models import Tag
from .request import _validate_request
from .types import ParametersTuple
from .types import ResponseDict

if sys.version_info >= (3, 8):
    iscoroutinefunction = inspect.iscoroutinefunction
else:
    def iscoroutinefunction(func: Any) -> bool:
        while inspect.ismethod(func):
            func = func.__func__

        while isinstance(func, functools.partial):
            func = func.func

        return inspect.iscoroutinefunction(func)

warnings.simplefilter("once")


class APIScaffold(Scaffold, ABC):
    def _collect_openapi_info(
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
            responses: Optional[ResponseDict] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> ParametersTuple:
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
            async def view_func(**kwargs) -> FlaskResponse:
                func_kwargs = _validate_request(
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    path_kwargs=kwargs
                )

                # handle async request
                if view_class:
                    signature = inspect.signature(view_class.__init__)
                    parameters = signature.parameters
                    if parameters.get("view_kwargs"):
                        view_object = view_class(view_kwargs=view_kwargs)
                    else:
                        view_object = view_class()
                    response = await func(view_object, **func_kwargs)
                else:
                    response = await func(**func_kwargs)
                return response
        else:
            @wraps(func)
            def view_func(**kwargs) -> FlaskResponse:
                func_kwargs = _validate_request(
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    path_kwargs=kwargs
                )

                # handle request
                if view_class:
                    signature = inspect.signature(view_class.__init__)
                    parameters = signature.parameters
                    if parameters.get("view_kwargs"):
                        view_object = view_class(view_kwargs=view_kwargs)
                    else:
                        view_object = view_class()
                    response = func(view_object, **func_kwargs)
                else:
                    response = func(**func_kwargs)
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
            responses: Optional[ResponseDict] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP GET method.
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: **Deprecated in v3.x**. Extra information describing the request body(application/form).
            extra_body: **Deprecated in v3.x**. Extra information describing the request body(application/json).
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            extra_responses: **Deprecated in v3.x**. Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        if extra_form is not None:
            warnings.warn(
                """`extra_form` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_body is not None:
            warnings.warn(
                """`extra_body` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_responses is not None:
            warnings.warn(
                """`extra_responses` will be deprecated in v3.x, please use `responses` instead.""",
                DeprecationWarning)

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._collect_openapi_info(
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
                    openapi_extensions=openapi_extensions,
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
            responses: Optional[ResponseDict] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP POST method.
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: **Deprecated in v3.x**. Extra information describing the request body(application/form).
            extra_body: **Deprecated in v3.x**. Extra information describing the request body(application/json).
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            extra_responses: **Deprecated in v3.x**. Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """
        if extra_form is not None:
            warnings.warn(
                """`extra_form` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_body is not None:
            warnings.warn(
                """`extra_body` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_responses is not None:
            warnings.warn(
                """`extra_responses` will be deprecated in v3.x, please use `responses` instead.""",
                DeprecationWarning)

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._collect_openapi_info(
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
                    openapi_extensions=openapi_extensions,
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
            responses: Optional[ResponseDict] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP PUT method.
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: **Deprecated in v3.x**. Extra information describing the request body(application/form).
            extra_body: **Deprecated in v3.x**. Extra information describing the request body(application/json).
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            extra_responses: **Deprecated in v3.x**. Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """
        if extra_form is not None:
            warnings.warn(
                """`extra_form` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_body is not None:
            warnings.warn(
                """`extra_body` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_responses is not None:
            warnings.warn(
                """`extra_responses` will be deprecated in v3.x, please use `responses` instead.""",
                DeprecationWarning)

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._collect_openapi_info(
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
                    openapi_extensions=openapi_extensions,
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
            responses: Optional[ResponseDict] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP DELETE method.
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: **Deprecated in v3.x**. Extra information describing the request body(application/form).
            extra_body: **Deprecated in v3.x**. Extra information describing the request body(application/json).
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            extra_responses: **Deprecated in v3.x**. Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """
        if extra_form is not None:
            warnings.warn(
                """`extra_form` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_body is not None:
            warnings.warn(
                """`extra_body` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_responses is not None:
            warnings.warn(
                """`extra_responses` will be deprecated in v3.x, please use `responses` instead.""",
                DeprecationWarning)

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._collect_openapi_info(
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
                    openapi_extensions=openapi_extensions,
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
            responses: Optional[ResponseDict] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP PATCH method.
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: **Deprecated in v3.x**. Extra information describing the request body(application/form).
            extra_body: **Deprecated in v3.x**. Extra information describing the request body(application/json).
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            extra_responses: **Deprecated in v3.x**. Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """
        if extra_form is not None:
            warnings.warn(
                """`extra_form` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_body is not None:
            warnings.warn(
                """`extra_body` will be deprecated in v3.x, please use `openapi_extra` instead.""",
                DeprecationWarning)
        if extra_responses is not None:
            warnings.warn(
                """`extra_responses` will be deprecated in v3.x, please use `responses` instead.""",
                DeprecationWarning)

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = \
                self._collect_openapi_info(
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
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PATCH
                )

            view_func = self.create_view_func(func, header, cookie, path, query, form, body)
            options.update({"methods": [HTTPMethod.PATCH]})
            self.add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/8/30 9:40
import inspect
from functools import wraps
from typing import Callable, Optional, Any

from flask.wrappers import Response as FlaskResponse
from flask import current_app, Response as _Response
from http import HTTPStatus
from pydantic import BaseModel
from typing import Type, Dict

from .models import ExternalDocumentation
from .models import Server
from .models import Tag
from .request import _validate_request
from .types import ParametersTuple
from .types import ResponseDict
from .utils import HTTPMethod


def is_response_validation_enabled(validate_response: Optional[bool] = None, api_validate_response: Optional[bool] = None):
    """
    Check if response validation is applicable. 

    If different levels are set, priority follows this order
        1. Set at the api/route/single endpoint (api_response_validate)
        2. Set at APIBlueprint creation (response_validate)
        3. Set at OpenAPI creation (response_validate)
        4. Set in config `FLASK_OPENAPI_VALIDATE_RESPONSE`

    NOTE: #2 and #3 come from response_validate.
    NOTE: What about APIView; should we not be able to set there as well?
    NOTE: Should there be any inheritance this validation, IE: nested ABPs?

    Args:
        response_validate: Whether the App/API-Blueprint wants to validate responses (context dependant)
        route_response_validate: Whether the route wants to validate responses
    """

    global_response_validate: bool = current_app.config.get("FLASK_OPENAPI_VALIDATE_RESPONSE", False)

    if api_validate_response:
        return True

    if validate_response:
        return True
    
    return global_response_validate
    

# def run_validate_response(resp: Any, responses: Optional[Dict[str, Type[BaseModel]]] = None) -> None:
def run_validate_response(resp: Any, responses: Optional[ResponseDict] = None) -> None:
    """Validate response"""

    # TODO: strict-mode? if a response is json and doesn't have a response status as well as not having
    # a model to validate this should be flagged as an issue? which would necessitate the response
    # to always return the correct/supported statuses as defined in "resposnes"

    warn = not current_app.config.get("FLASK_OPENAPI_DISABLE_WARNINGS", False)

    if warn:
        print("Warning: "
              "You are using `FLASK_OPENAPI_VALIDATE_RESPONSE=True`, "
              "please do not use it in the production environment, "
              "because it will reduce the performance. "
              "NOTE, you can disable this warning with `Flask.config['FLASK_OPENAPI_DISABLE_WARNINGS'] = True`")


    if not responses:
        print("Warning, response validation on but endpoint has no responses set")
        return

    if isinstance(resp, tuple):  # noqa
        _resp, status_code = resp[:2]

    elif isinstance(resp, _Response):
        if resp.mimetype != "application/json":
            # only application/json
            return
            # raise TypeError("`Response` mimetype must be application/json.")
        _resp, status_code = resp.json, resp.status_code  # noqa

    else:
        _resp, status_code = resp, 200

    # status_code is http.HTTPStatus
    if isinstance(status_code, HTTPStatus):
        status_code = status_code.value

    resp_model = responses.get(status_code)

    if resp_model is None:
        if warn:
            print("Warning: missing status code map to `pydantic.BaseModel`")

        return

    assert inspect.isclass(resp_model) and \
           issubclass(resp_model, BaseModel), f"{resp_model} is invalid `pydantic.BaseModel`"

    if isinstance(_resp, str):
        resp_model.model_validate_json(_resp)

    elif not isinstance(_resp, dict):
        resp_model.model_validate(_resp)

    else:
        try:
            resp_model(**_resp)

        except TypeError:
            raise TypeError(f"`{resp_model.__name__}` validation failed, must be a mapping.")


class APIScaffold:
    def _collect_openapi_info(
            self,
            rule: str,
            func: Callable,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> ParametersTuple:
        raise NotImplementedError   # pragma: no cover

    def register_api(self, api) -> None:
        raise NotImplementedError   # pragma: no cover

    def _add_url_rule(
            self,
            rule,
            endpoint=None,
            view_func=None,
            provide_automatic_options=None,
            **options,
    ) -> None:
        raise NotImplementedError   # pragma: no cover

    @staticmethod
    def create_view_func(
            # self,
            func,
            header,
            cookie,
            path,
            query,
            form,
            body,
            raw,
            responses: Optional[ResponseDict] = None,
            view_class=None,
            view_kwargs=None,
            parent_validate_response: Optional[bool] = None,
            api_validate_response: Optional[bool] = None,
    ):

        is_coroutine_function = inspect.iscoroutinefunction(func)
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
                    raw=raw,
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

                if is_response_validation_enabled(validate_response=parent_validate_response, api_validate_response=api_validate_response) and responses:
                    run_validate_response(response, responses)

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
                    raw=raw,
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

                if is_response_validation_enabled(validate_response=parent_validate_response, api_validate_response=api_validate_response):
                    run_validate_response(response, responses)

                return response

        if not hasattr(func, "view"):
            func.view = view_func

        return func.view

    def get(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            validate_response: Optional[bool] = None,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP GET method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.GET
                )

            parent_validate_response = self.get_parent_validation()
            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw, responses=responses, parent_validate_response=parent_validate_response, api_validate_response=validate_response)

            options.update({"methods": [HTTPMethod.GET]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def post(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            validate_response: bool = False,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP POST method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.POST
                )

            parent_validate_response = self.get_parent_validation()
            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw, responses=responses, parent_validate_response=parent_validate_response, api_validate_response=validate_response)

            options.update({"methods": [HTTPMethod.POST]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def put(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            validate_response: bool = False,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP PUT method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PUT
                )

            parent_validate_response = self.get_parent_validation()
            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw, responses=responses, parent_validate_response=parent_validate_response, api_validate_response=validate_response)

            options.update({"methods": [HTTPMethod.PUT]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def delete(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            validate_response: bool = False,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP DELETE method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.DELETE
                )

            parent_validate_response = self.get_parent_validation()
            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw, responses=responses, parent_validate_response=parent_validate_response, api_validate_response=validate_response)

            options.update({"methods": [HTTPMethod.DELETE]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def patch(
            self,
            rule: str,
            *,
            tags: Optional[list[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[list[dict[str, list[Any]]]] = None,
            servers: Optional[list[Server]] = None,
            openapi_extensions: Optional[dict[str, Any]] = None,
            doc_ui: bool = True,
            validate_response: bool = False,
            **options: Any
    ) -> Callable:
        """
        Decorator for defining a REST API endpoint with the HTTP PATCH method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, raw = \
                self._collect_openapi_info(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    external_docs=external_docs,
                    operation_id=operation_id,
                    responses=responses,
                    deprecated=deprecated,
                    security=security,
                    servers=servers,
                    openapi_extensions=openapi_extensions,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PATCH
                )

            parent_validate_response = self.get_parent_validation()
            view_func = self.create_view_func(func, header, cookie, path, query, form, body, raw, responses=responses, parent_validate_response=parent_validate_response, api_validate_response=validate_response)

            options.update({"methods": [HTTPMethod.PATCH]})
            self._add_url_rule(rule, view_func=view_func, **options)

            return func

        return decorator

    def get_parent_validation(self):
        # NOTE: abp_ vs app_ distinction without a difference in this context?
        if hasattr(self, "abp_validate_response"):
            return self.abp_validate_response
    
        return self.app_validate_response

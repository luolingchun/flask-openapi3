# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/10/14 16:09
import re
import typing
import warnings

if typing.TYPE_CHECKING:
    from .openapi import OpenAPI

from copy import deepcopy
from typing import Optional, List, Dict, Type, Any, Callable, Union

from pydantic import BaseModel

from .http import HTTPMethod
from .models.common import ExternalDocumentation, ExtraRequestBody
from .models.server import Server
from .models.tag import Tag
from .utils import get_operation, parse_and_store_tags, parse_parameters, get_responses, parse_method, \
    get_operation_id_for_path

warnings.simplefilter("once")


class APIView:
    def __init__(
            self,
            url_prefix: Optional[str] = None,
            view_tags: Optional[List[Tag]] = None,
            view_security: Optional[List[Dict[str, List[str]]]] = None,
            view_responses: Optional[Dict[str, Union[Type[BaseModel], Dict[Any, Any], None]]] = None,
            doc_ui: bool = True,
            operation_id_callback: Callable = get_operation_id_for_path,
    ):
        """
        Create a class-based view

        Arguments:
            url_prefix: A path to prepend to all the APIView's urls
            view_tags: APIView tags for every API.
            view_security: APIView security for every API.
            view_responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Enable OpenAPI document UI (Swagger UI and Redoc). Defaults to True.
            operation_id_callback: Callback function for custom operation_id generation.
                                   Receives name (str), path (str) and method (str) parameters.
                                   Default to `get_operation_id_for_path` from utils
        """
        self.url_prefix = url_prefix
        self.view_tags = view_tags or []
        self.view_security = view_security or []
        self.view_responses = view_responses or {}
        self.doc_ui = doc_ui
        self.operation_id_callback: Callable = operation_id_callback

        self.views: Dict = dict()
        self.paths: Dict = dict()
        self.components_schemas: Dict = dict()
        self.tags: List[Tag] = []
        self.tag_names: List[str] = []

    def route(self, rule: str):
        """Decorator for view class"""

        def wrapper(cls):
            if self.views.get(rule):
                raise ValueError(f"malformed url rule: {rule!r}")
            methods = []
            # Convert route parameter format from /pet/<petId> to /pet/{petId}
            uri = re.sub(r"<([^<:]+:)?", "{", rule).replace(">", "}")
            trail_slash = uri.endswith("/")
            # Merge url_prefix and uri
            uri = self.url_prefix.rstrip("/") + "/" + uri.lstrip("/") if self.url_prefix else uri
            if not trail_slash:
                uri = uri.rstrip("/")
            for method in HTTPMethod:
                cls_method = getattr(cls, method.lower(), None)
                if not cls_method:
                    continue
                methods.append(method)
                if self.doc_ui is False:
                    continue
                if not getattr(cls_method, "operation", None):
                    continue
                # Parse method
                parse_method(uri, method, self.paths, cls_method.operation)
                # Update operation_id
                if not cls_method.operation.operationId:
                    cls_method.operation.operationId = self.operation_id_callback(
                        name=cls_method.__qualname__,
                        path=rule,
                        method=method
                    )
            # Convert route parameters from <param> to {param}
            _rule = uri.replace("{", "<").replace("}", ">")
            self.views[_rule] = (cls, methods)

            return cls

        return wrapper

    def doc(
            self,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id: Optional[str] = None,
            extra_form: Optional[ExtraRequestBody] = None,
            extra_body: Optional[ExtraRequestBody] = None,
            responses: Optional[Dict[str, Union[Type[BaseModel], Dict[Any, Any], None]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True
    ) -> Callable:
        """
        Decorator for view method.
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            extra_form: Extra information describing the request body(application/form).
            extra_body: Extra information describing the request body(application/json).
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Add openapi document UI (swagger, rapidoc, and redoc).
                    Default to True.
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

        if responses is None:
            responses = {}
        if extra_responses is None:
            extra_responses = {}
        if security is None:
            security = []
        tags = tags + self.view_tags if tags else self.view_tags

        def decorator(func):
            if self.doc_ui is False or doc_ui is False:
                return
            # Global response combines API responses
            combine_responses = deepcopy(self.view_responses)
            combine_responses.update(**responses)
            # Create operation
            operation = get_operation(
                func,
                summary=summary,
                description=description,
                openapi_extensions=openapi_extensions
            )
            # Set external docs
            operation.externalDocs = external_docs
            # Unique string used to identify the operation.
            operation.operationId = operation_id
            # Only set `deprecated` if True, otherwise leave it as None
            operation.deprecated = deprecated
            # Add security
            operation.security = security + self.view_security or None
            # Add servers
            operation.servers = servers
            # Store tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)
            # Parse parameters
            parse_parameters(
                func,
                extra_form=extra_form,
                extra_body=extra_body,
                components_schemas=self.components_schemas,
                operation=operation
            )
            # Parse response
            get_responses(combine_responses, extra_responses, self.components_schemas, operation)
            func.operation = operation

            return func

        return decorator

    def register(self, app: "OpenAPI", view_kwargs: Optional[Dict[Any, Any]] = None):
        """
        Register the API views with the given OpenAPI app.

        Args:
            app: An instance of the OpenAPI app.
            view_kwargs: Additional keyword arguments to pass to the API views.
        """
        if view_kwargs is None:
            view_kwargs = {}
        for rule, (cls, methods) in self.views.items():
            for method in methods:
                func = getattr(cls, method.lower())
                header, cookie, path, query, form, body = parse_parameters(func, doc_ui=False)
                view_func = app.create_view_func(
                    func,
                    header,
                    cookie,
                    path,
                    query,
                    form,
                    body,
                    view_class=cls,
                    view_kwargs=view_kwargs
                )
                options = {
                    "endpoint": cls.__name__ + "." + method.lower(),
                    "methods": [method.upper()]
                }
                app.add_url_rule(rule, view_func=view_func, **options)

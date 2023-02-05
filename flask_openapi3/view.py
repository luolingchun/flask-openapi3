# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/10/14 16:09
import re
import typing

if typing.TYPE_CHECKING:
    from .openapi import OpenAPI

from copy import deepcopy
from typing import Optional, List, Dict, Type, Any, Callable

from pydantic import BaseModel

from .http import HTTPMethod
from .models.common import ExternalDocumentation, ExtraRequestBody
from .models.server import Server
from .models.tag import Tag
from .utils import get_operation, parse_and_store_tags, parse_parameters, get_responses, parse_method, \
    get_operation_id_for_path


class APIView:
    def __init__(
            self,
            url_prefix: Optional[str] = None,
            view_tags: Optional[List[Tag]] = None,
            view_security: Optional[List[Dict[str, List[str]]]] = None,
            view_responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            doc_ui: bool = True
    ):
        """
        Create a class-based view

        Arguments:
            url_prefix: A path to prepend to all the APIView's urls
            view_tags: APIView tags for every api
            view_security: APIView security for every api
            view_responses: APIView response models
            doc_ui: Add openapi document UI(swagger, rapidoc and redoc). Defaults to True.
        """
        self.url_prefix = url_prefix
        self.view_tags = view_tags or []
        self.view_security = view_security or []
        self.view_responses = view_responses or {}
        self.doc_ui = doc_ui

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
            # /pet/<petId> --> /pet/{petId}
            uri = re.sub(r"<([^<:]+:)?", "{", rule).replace(">", "}")
            trail_slash = uri.endswith("/")
            # merge url_prefix and uri
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
                # parse method
                parse_method(uri, method, self.paths, cls_method.operation)
                # update operation_id
                if not cls_method.operation.operationId:
                    cls_method.operation.operationId = get_operation_id_for_path(
                        name=cls_method.__qualname__,
                        path=rule,
                        method=method
                    )
            # /pet/{petId} --> /pet/<petId>
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
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
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
            responses: Responses model, must be pydantic BaseModel.
            extra_responses: Extra information for responses.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            doc_ui: Declares this operation to be show.
        """

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
            # global response combine api responses
            combine_responses = deepcopy(self.view_responses)
            combine_responses.update(**responses)
            # create operation
            operation = get_operation(func, summary=summary, description=description)
            # set external docs
            operation.externalDocs = external_docs
            # Unique string used to identify the operation.
            operation.operationId = operation_id
            # only set `deprecated` if True otherwise leave it as None
            operation.deprecated = deprecated
            # add security
            operation.security = security + self.view_security or None
            # add servers
            operation.servers = servers
            # store tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)
            # parse parameters
            parse_parameters(
                func,
                extra_form=extra_form,
                extra_body=extra_body,
                components_schemas=self.components_schemas,
                operation=operation
            )
            # parse response
            get_responses(combine_responses, extra_responses, self.components_schemas, operation)
            func.operation = operation

            return func

        return decorator

    def register(self, app: "OpenAPI"):
        for rule, (cls, methods) in self.views.items():
            for method in methods:
                func = getattr(cls, method.lower())
                header, cookie, path, query, form, body = parse_parameters(func, doc_ui=False)
                view_func = app.create_view_func(func, header, cookie, path, query, form, body, view_class=cls)
                options = {
                    "endpoint": cls.__name__ + "." + method.lower(),
                    "methods": [method.upper()]
                }
                app.add_url_rule(rule, view_func=view_func, **options)

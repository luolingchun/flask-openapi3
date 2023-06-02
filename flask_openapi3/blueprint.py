# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/1 16:54
import re
from copy import deepcopy
from typing import Optional, List, Dict, Any, Type, Callable, Tuple, Union

from flask import Blueprint
from pydantic import BaseModel

from .http import HTTPMethod
from .models import Tag, ExternalDocumentation
from .models.common import ExtraRequestBody
from .models.server import Server
from .scaffold import APIScaffold
from .utils import get_operation, get_responses, parse_and_store_tags, parse_parameters, parse_method, \
    get_operation_id_for_path


class APIBlueprint(APIScaffold, Blueprint):
    def __init__(
            self,
            name: str,
            import_name: str,
            *,
            abp_tags: Optional[List[Tag]] = None,
            abp_security: Optional[List[Dict[str, List[str]]]] = None,
            abp_responses: Optional[Dict[str, Union[Type[BaseModel], Dict[Any, Any], None]]] = None,
            doc_ui: bool = True,
            operation_id_callback: Callable = get_operation_id_for_path,
            **kwargs: Any
    ) -> None:
        """
        Based on Flask Blueprint

        Arguments:
            name: The name of the blueprint. It Will be prepared to each endpoint name.
            import_name: The name of the blueprint package, usually ``__name__``.
                         This helps locate the ``root_path`` for the blueprint.
            abp_tags: APIBlueprint tags for every API.
            abp_security: APIBlueprint security for every API.
            abp_responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Enable OpenAPI document UI (Swagger UI, Redoc and Rapidoc). Defaults to True.
            operation_id_callback: Callback function for custom operation_id generation.
                                   Receives name (str), path (str) and method (str) parameters.
                                   Defaults to `get_operation_id_for_path` from utils
            **kwargs: Flask Blueprint kwargs
        """
        super(APIBlueprint, self).__init__(name, import_name, **kwargs)

        # Initialize instance variables
        self.paths: Dict = dict()
        self.components_schemas: Dict = dict()
        self.tags: List[Tag] = []
        self.tag_names: List[str] = []

        # Set values from arguments or default values
        self.abp_tags = abp_tags or []
        self.abp_security = abp_security or []
        self.abp_responses = abp_responses or {}
        self.doc_ui = doc_ui

        # Set the operation ID callback function
        self.operation_id_callback: Callable = operation_id_callback

    def register_api(self, api: "APIBlueprint") -> None:
        """Register a nested APIBlueprint"""

        # Check if the APIBlueprint is being registered on itself
        if api is self:
            raise ValueError("Cannot register a api blueprint on itself")

        # Merge tags from the nested APIBlueprint
        for tag in api.tags:
            if tag.name not in self.tag_names:
                self.tags.append(tag)

        # Merge paths from the nested APIBlueprint
        for path_url, path_item in api.paths.items():
            trail_slash = path_url.endswith("/")

            # Merge url_prefix and new API blueprint path url
            uri = self.url_prefix.rstrip("/") + "/" + path_url.lstrip("/") if self.url_prefix else path_url

            # Strip the right slash
            if not trail_slash:
                uri = uri.rstrip("/")

            self.paths[uri] = path_item

        # Merge component schemas from the nested APIBlueprint
        self.components_schemas.update(**api.components_schemas)

        # Register the nested APIBlueprint as a blueprint
        self.register_blueprint(api)

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
            responses: Optional[Dict[str, Union[Type[BaseModel], Dict[Any, Any], None]]] = None,
            extra_responses: Optional[Dict[str, Dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel]]:
        """
        Collects OpenAPI specification information for Flask routes and view functions.

        Arguments:
            rule: Flask route
            func: Flask view_func
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
            doc_ui: Add openapi document UI(swagger, rapidoc and redoc). Defaults to True.
        """
        if self.doc_ui is True and doc_ui is True:
            if responses is None:
                responses = {}
            if extra_responses is None:
                extra_responses = {}
            # Global response: combine API responses
            combine_responses = deepcopy(self.abp_responses)
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
            operation.operationId = operation_id or self.operation_id_callback(
                name=func.__name__, path=rule, method=method
            )
            # Only set `deprecated` if True, otherwise leave it as None
            operation.deprecated = deprecated
            # Add security
            if security is None:
                security = []
            operation.security = security + self.abp_security or None
            # Add servers
            operation.servers = servers
            # Store tags
            tags = tags + self.abp_tags if tags else self.abp_tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)
            # Parse parameters
            header, cookie, path, query, form, body = parse_parameters(
                func,
                extra_form=extra_form,
                extra_body=extra_body,
                components_schemas=self.components_schemas,
                operation=operation
            )
            # Parse response
            get_responses(combine_responses, extra_responses, self.components_schemas, operation)
            # Convert route parameter format from /pet/<petId> to /pet/{petId}
            uri = re.sub(r"<([^<:]+:)?", "{", rule).replace(">", "}")
            trail_slash = uri.endswith("/")
            # Merge url_prefix and uri
            uri = self.url_prefix.rstrip("/") + "/" + uri.lstrip("/") if self.url_prefix else uri
            if not trail_slash:
                uri = uri.rstrip("/")
            # Parse method
            parse_method(uri, method, self.paths, operation)
            return header, cookie, path, query, form, body
        else:
            # Parse parameters
            header, cookie, path, query, form, body = parse_parameters(func, doc_ui=False)
            return header, cookie, path, query, form, body

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/4/1 16:54
from copy import deepcopy
from typing import Optional, List, Dict, Any, Callable

from flask import Blueprint

from .models import ExternalDocumentation
from .models import Server
from .models import Tag
from .scaffold import APIScaffold
from .types import ParametersTuple
from .types import ResponseDict
from .utils import HTTPMethod
from .utils import convert_responses_key_to_string
from .utils import get_operation
from .utils import get_operation_id_for_path
from .utils import get_responses
from .utils import parse_and_store_tags
from .utils import parse_method
from .utils import parse_parameters
from .utils import parse_rule


class APIBlueprint(APIScaffold, Blueprint):
    def __init__(
            self,
            name: str,
            import_name: str,
            *,
            abp_tags: Optional[List[Tag]] = None,
            abp_security: Optional[List[Dict[str, List[str]]]] = None,
            abp_responses: Optional[ResponseDict] = None,
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
            doc_ui: Enable OpenAPI document UI (Swagger UI, Redoc, and Rapidoc). Defaults to True.
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

        abp_responses = abp_responses or {}
        # Convert key to string
        self.abp_responses = convert_responses_key_to_string(abp_responses)

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
            # Parse rule: merge url_prefix and format rule from /pet/<petId> to /pet/{petId}
            uri = parse_rule(path_url, url_prefix=self.url_prefix)

            self.paths[uri] = path_item

        # Merge component schemas from the nested APIBlueprint
        self.components_schemas.update(**api.components_schemas)

        # Register the nested APIBlueprint as a blueprint
        self.register_blueprint(api)

    def _add_url_rule(
            self,
            rule,
            endpoint=None,
            view_func=None,
            provide_automatic_options=None,
            **options,
    ) -> None:
        self.add_url_rule(rule, endpoint, view_func, provide_automatic_options, **options)

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
            responses: Optional[ResponseDict] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> ParametersTuple:
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
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            doc_ui: Declares this operation to be shown. Default to True.
        """
        if self.doc_ui is True and doc_ui is True:
            if responses is None:
                new_responses = {}
            else:
                # Convert key to string
                new_responses = convert_responses_key_to_string(responses)
            # Global response: combine API responses
            combine_responses = deepcopy(self.abp_responses)
            combine_responses.update(**new_responses)
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
            header, cookie, path, query, form, body, raw = parse_parameters(
                func,
                components_schemas=self.components_schemas,
                operation=operation
            )
            # Parse response
            get_responses(combine_responses, self.components_schemas, operation)

            # Parse rule: merge url_prefix and format rule from /pet/<petId> to /pet/{petId}
            uri = parse_rule(rule, url_prefix=self.url_prefix)

            # Parse method
            parse_method(uri, method, self.paths, operation)
            return header, cookie, path, query, form, body, raw
        else:
            # Parse parameters
            header, cookie, path, query, form, body, raw = parse_parameters(func, doc_ui=False)
            return header, cookie, path, query, form, body, raw

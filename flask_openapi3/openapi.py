# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:25
import json
import os
import re
from copy import deepcopy
from typing import Optional, List, Dict, Union, Any, Type, Callable

from flask import Flask, Blueprint, render_template_string
from pydantic import BaseModel

from .blueprint import APIBlueprint
from .commands import openapi_command
from .models import APISpec
from .models import Components
from .models import ExternalDocumentation
from .models import Info
from .models import OAuthConfig
from .models import OPENAPI3_REF_PREFIX
from .models import Schema
from .models import Server
from .models import Tag
from .models import ValidationErrorModel
from .scaffold import APIScaffold
from .templates import openapi_html_string
from .templates import rapidoc_html_string
from .templates import redoc_html_string
from .templates import swagger_html_string
from .types import ParametersTuple
from .types import ResponseDict
from .types import SecuritySchemesDict
from .utils import HTTPMethod
from .utils import HTTP_STATUS
from .utils import convert_responses_key_to_string
from .utils import get_model_schema
from .utils import get_operation
from .utils import get_operation_id_for_path
from .utils import get_responses
from .utils import make_validation_error_response
from .utils import parse_and_store_tags
from .utils import parse_method
from .utils import parse_parameters
from .view import APIView


class OpenAPI(APIScaffold, Flask):
    def __init__(
            self,
            import_name: str,
            *,
            info: Optional[Info] = None,
            security_schemes: Optional[SecuritySchemesDict] = None,
            oauth_config: Optional[OAuthConfig] = None,
            responses: Optional[ResponseDict] = None,
            doc_ui: bool = True,
            doc_expansion: str = "list",
            doc_prefix: str = "/openapi",
            api_doc_url: str = "/openapi.json",
            swagger_url: str = "/swagger",
            redoc_url: str = "/redoc",
            rapidoc_url: str = "/rapidoc",
            swagger_config: Optional[Dict[str, Any]] = None,
            ui_templates: Optional[Dict[str, str]] = None,
            servers: Optional[List[Server]] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            operation_id_callback: Callable = get_operation_id_for_path,
            openapi_extensions: Optional[Dict[str, Any]] = None,
            validation_error_status: Union[str, int] = 422,
            validation_error_model: Type[BaseModel] = ValidationErrorModel,
            validation_error_callback: Callable = make_validation_error_response,
            **kwargs: Any
    ) -> None:
        """
        OpenAPI class that provides REST API functionality along with Swagger UI and Redoc.

        Args:
            import_name: The import name for the Flask application.
            info: Information about the API (title, version, etc.).
                  See https://spec.openapis.org/oas/v3.1.0#info-object.
            security_schemes: Security schemes for the API.
                              See https://spec.openapis.org/oas/v3.1.0#security-scheme-object.
            oauth_config: OAuth 2.0 configuration for authentication.
                          See https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Enable OpenAPI document UI (Swagger UI and Redoc). Defaults to True.
            doc_expansion(deprecated): Default expansion setting for operations and tags ("list", "full", or "none").
                           See https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md.
            doc_prefix: URL prefix used for OpenAPI document and UI. Defaults to "/openapi"
            api_doc_url: URL for accessing the OpenAPI specification document in JSON format.
                         Defaults to "/openapi.json".
            swagger_url: URL for accessing the Swagger UI documentation. Defaults to "/swagger".
            redoc_url: URL for accessing the Redoc UI documentation. Defaults to "/redoc".
            rapidoc_url: URL for accessing the RapiDoc UI documentation. Defaults to "/rapidoc".
            swagger_config: Swagger UI Configuration, More information:
                            https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md.
            ui_templates: Custom UI templates to override or add UI documents.
            servers: An array of Server objects providing connectivity information to a target server.
            external_docs: External documentation for the API.
                           See: https://spec.openapis.org/oas/v3.1.0#external-documentation-object.
            operation_id_callback: Callback function for custom operation ID generation.
                                   Receives name (str), path (str), and method (str) parameters.
                                   Defaults to `get_operation_id_for_path` from utils.
            openapi_extensions: Extensions to the OpenAPI Schema.
                                See https://spec.openapis.org/oas/v3.1.0#specification-extensions.
            validation_error_status: HTTP Status of the response given when a validation error is detected by pydantic.
                                    Defaults to 422.
            validation_error_model: Validation error response model for OpenAPI Specification.
            validation_error_callback: Validation error response callback, the return format corresponds to
                                       the validation_error_model.
            **kwargs: Additional kwargs to be passed to Flask.
        """
        super(OpenAPI, self).__init__(import_name, **kwargs)

        # Set OpenAPI version and API information
        self.openapi_version = "3.1.0"
        self.info = info or Info(title="OpenAPI", version="1.0.0")

        # Set security schemes, responses, paths and components
        self.security_schemes = security_schemes

        responses = responses or {}
        # Convert key to string
        self.responses = convert_responses_key_to_string(responses)

        self.paths: Dict = dict()
        self.components_schemas: Dict = dict()
        self.components = Components()

        # Initialize lists for tags and tag names
        self.tags: List[Tag] = []
        self.tag_names: List[str] = []

        # Set URL prefixes and endpoints
        self.doc_prefix = doc_prefix
        self.api_doc_url = api_doc_url
        self.swagger_url = swagger_url
        self.redoc_url = redoc_url
        self.rapidoc_url = rapidoc_url

        # Set OAuth configuration and documentation expansion
        self.oauth_config = oauth_config
        if doc_expansion != "list":
            import warnings
            warnings.filterwarnings("once")
            warnings.warn("The `doc_expansion` parameter is deprecated; use `swagger_config` instead.",
                          DeprecationWarning)
        self.doc_expansion = doc_expansion
        self.swagger_config = swagger_config

        # Set UI templates for customization
        self.ui_templates = ui_templates or dict()

        # Set servers and external documentation
        self.severs = servers
        self.external_docs = external_docs

        # Set the operation ID callback function
        self.operation_id_callback: Callable = operation_id_callback

        # Set OpenAPI extensions
        self.openapi_extensions = openapi_extensions or dict()

        # Set HTTP Response of validation errors within OpenAPI
        self.validation_error_status = str(validation_error_status)
        self.validation_error_model = validation_error_model
        self.validation_error_callback = validation_error_callback

        # Initialize the OpenAPI documentation UI
        if doc_ui:
            self._init_doc()

        # Add the OpenAPI command
        self.cli.add_command(openapi_command)

        # Initialize specification JSON
        self.spec_json: Dict = dict()

    def _init_doc(self) -> None:
        """
        Provide Swagger UI, Redoc, and Rapidoc
        """
        _here = os.path.dirname(__file__)
        template_folder = os.path.join(_here, "templates")
        static_folder = os.path.join(template_folder, "static")

        # Create the blueprint for OpenAPI documentation
        blueprint = Blueprint(
            "openapi",
            __name__,
            url_prefix=self.doc_prefix,
            template_folder=template_folder,
            static_folder=static_folder
        )

        # Add the API documentation URL rule
        blueprint.add_url_rule(
            rule=self.api_doc_url,
            endpoint="api_doc",
            view_func=lambda: self.api_doc
        )

        # Combine built-in templates and user-defined templates
        builtins_templates = {
            self.swagger_url.strip("/"): swagger_html_string,
            self.redoc_url.strip("/"): redoc_html_string,
            self.rapidoc_url.strip("/"): rapidoc_html_string,
            **self.ui_templates
        }

        # Add URL rules for the templates
        for key, value in builtins_templates.items():
            blueprint.add_url_rule(
                rule=f"/{key}",
                endpoint=key,
                # Pass default value to source
                view_func=lambda source=value: render_template_string(
                    source,
                    api_doc_url=self.api_doc_url.lstrip("/"),
                    # The following parameters are only for swagger ui
                    doc_expansion=self.doc_expansion,
                    swagger_config=self.swagger_config,
                    oauth_config=self.oauth_config.model_dump() if self.oauth_config else None
                )
            )

        # Add URL rule for the home page
        blueprint.add_url_rule(
            rule="/",
            endpoint="openapi",
            view_func=lambda: render_template_string(
                openapi_html_string,
                swagger_url=self.swagger_url.lstrip("/"),
                redoc_url=self.redoc_url.lstrip("/"),
                rapidoc_url=self.rapidoc_url.lstrip("/")
            )
        )

        # Register the blueprint with the Flask application
        self.register_blueprint(blueprint)

    @property
    def api_doc(self) -> Dict:
        """
        Generate the OpenAPI specification JSON.

        Returns:
            The OpenAPI specification JSON as a dictionary.

        """
        if self.spec_json:
            return self.spec_json

        spec = APISpec(
            openapi=self.openapi_version,
            info=self.info,
            servers=self.severs,
            paths=self.paths,
            externalDocs=self.external_docs
        )
        # Set tags
        spec.tags = self.tags or None

        # Add ValidationErrorModel to components schemas
        schema = get_model_schema(self.validation_error_model)
        self.components_schemas[self.validation_error_model.__name__] = Schema(**schema)

        # Parse definitions
        definitions = schema.get("$defs", {})
        for name, value in definitions.items():
            self.components_schemas[name] = Schema(**value)

        # Set components
        self.components.schemas = self.components_schemas
        self.components.securitySchemes = self.security_schemes
        spec.components = self.components

        # Convert spec to JSON
        self.spec_json = json.loads(spec.model_dump_json(by_alias=True, exclude_none=True, warnings=False))

        # Update with OpenAPI extensions
        self.spec_json.update(**self.openapi_extensions)

        # Handle validation error response
        for rule, path_item in self.spec_json["paths"].items():
            for http_method, operation in path_item.items():
                if operation.get("parameters") is None and operation.get("requestBody") is None:
                    continue
                if not operation.get("responses"):
                    operation["responses"] = {}
                if operation["responses"].get(self.validation_error_status):
                    continue
                operation["responses"][self.validation_error_status] = {
                    "description": HTTP_STATUS[self.validation_error_status],
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {"$ref": f"{OPENAPI3_REF_PREFIX}/{self.validation_error_model.__name__}"}
                            }
                        }
                    }
                }

        return self.spec_json

    def register_api(self, api: APIBlueprint) -> None:
        """
        Register an APIBlueprint.

        Args:
            api: The APIBlueprint instance to register.

        """
        for tag in api.tags:
            if tag.name not in self.tag_names:
                # Append tag to the list of tags
                self.tags.append(tag)
                # Append tag name to the list of tag names
                self.tag_names.append(tag.name)

        # Update paths with the APIBlueprint's paths
        self.paths.update(**api.paths)

        # Update component schemas with the APIBlueprint's component schemas
        self.components_schemas.update(**api.components_schemas)

        # Register the APIBlueprint with the current instance
        self.register_blueprint(api)

    def register_api_view(self, api_view: APIView, view_kwargs: Optional[Dict[Any, Any]] = None) -> None:
        """
        Register APIView

        Args:
            api_view: The APIView instance to register.
            view_kwargs: Additional keyword arguments to pass to the API views.
        """
        if view_kwargs is None:
            view_kwargs = {}

        # Iterate through tags of the APIView
        for tag in api_view.tags:
            if tag.name not in self.tag_names:
                # Append tag to the list of tags
                self.tags.append(tag)
                # Append tag name to the list of tag names
                self.tag_names.append(tag.name)

        # Update paths with the APIView's paths
        self.paths.update(**api_view.paths)

        # Update component schemas with the APIView's component schemas
        self.components_schemas.update(**api_view.components_schemas)

        # Register the APIView with the current instance
        api_view.register(self, view_kwargs=view_kwargs)

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

        Args:
            rule: Flask route.
            func: Flask view_func.
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
            method: HTTP method for the operation. Defaults to GET.
        """
        if doc_ui is True:
            if responses is None:
                new_responses = {}
            else:
                # Convert key to string
                new_responses = convert_responses_key_to_string(responses)
            # Global response: combine API responses
            combine_responses = deepcopy(self.responses)
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
            operation.security = security
            # Add servers
            operation.servers = servers
            # Store tags
            if tags is None:
                tags = []
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)
            # Parse parameters
            header, cookie, path, query, form, body, raw = parse_parameters(
                func,
                components_schemas=self.components_schemas,
                operation=operation
            )
            # Parse response
            get_responses(combine_responses, self.components_schemas, operation)
            # Convert a route parameter format from /pet/<petId> to /pet/{petId}
            uri = re.sub(r"<([^<:]+:)?", "{", rule).replace(">", "}")
            # Parse method
            parse_method(uri, method, self.paths, operation)
            return header, cookie, path, query, form, body, raw
        else:
            # Parse parameters
            header, cookie, path, query, form, body, raw = parse_parameters(func, doc_ui=False)
            return header, cookie, path, query, form, body, raw

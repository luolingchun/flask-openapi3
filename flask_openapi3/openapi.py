# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:25
import json
import os
import re
from copy import deepcopy
from typing import Optional, List, Dict, Union, Any, Type, Callable, Tuple

from flask import Flask, Blueprint, render_template
from pydantic import BaseModel

from .api_blueprint import APIBlueprint
from .commands import openapi_command
from .http import HTTPMethod
from .models import Info, APISpec, Tag, Components, Server
from .models.common import Reference, ExternalDocumentation, ExtraRequestBody
from .models.oauth import OAuthConfig
from .models.security import SecurityScheme
from .scaffold import _Scaffold
from .utils import get_operation, get_responses, parse_and_store_tags, parse_parameters, validate_responses_type, \
    parse_method, get_operation_id_for_path


class OpenAPI(_Scaffold, Flask):
    def __init__(
            self,
            import_name: str,
            *,
            info: Optional[Info] = None,
            security_schemes: Optional[Dict[str, Union[SecurityScheme, Reference]]] = None,
            oauth_config: Optional[OAuthConfig] = None,
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            doc_ui: bool = True,
            doc_expansion: str = "list",
            doc_prefix: str = "/openapi",
            api_doc_url: str = "/openapi.json",
            swagger_url: str = "/swagger",
            redoc_url: str = "/redoc",
            rapidoc_url: str = "/rapidoc",
            servers: Optional[List[Server]] = None,
            external_docs: Optional[ExternalDocumentation] = None,
            **kwargs: Any
    ) -> None:
        """
        Based on Flask. Provide REST api, swagger-ui and redoc.

        Arguments:
            import_name: Just flask import_name
            info: See https://spec.openapis.org/oas/v3.0.3#info-object
            security_schemes: See https://spec.openapis.org/oas/v3.0.3#security-scheme-object
            oauth_config: OAuth 2.0 configuration,
                          see https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md
            responses: OpenAPI response model
            doc_ui: Add openapi document UI(swagger and redoc). Defaults to True.
            doc_expansion: String=["list"*, "full", "none"].
                          Controls the default expansion setting for the operations and tags.
                          It can be "list" (expands only the tags),
                         "full" (expands the tags and operations) or "none" (expands nothing).
                         see https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md
            doc_prefix: URL prefix used for OpenAPI document and UI. Defaults to "/openapi".
            api_doc_url: The OpenAPI Spec documentation. Defaults to "/openapi.json".
            swagger_url: The Swagger UI documentation. Defaults to `/swagger`.
            redoc_url: The Redoc UI documentation. Defaults to `/redoc`.
            rapidoc_url: The RapiDoc UI documentation. Defaults to `/rapidoc`.
            servers: An array of Server Objects, which provide connectivity information to a target server.
            external_docs: Allows referencing an external resource for extended documentation.
                           See: https://spec.openapis.org/oas/v3.0.3#external-documentation-object
            **kwargs: Flask kwargs
        """
        super(OpenAPI, self).__init__(import_name, **kwargs)

        self.openapi_version = "3.0.3"
        if info is None:
            info = Info(title="OpenAPI", version="1.0.0")
        assert isinstance(info, Info), f"Info is required (got type {type(info)})"
        self.info = info
        self.security_schemes = security_schemes
        self.responses = responses or {}
        self.paths = dict()
        self.components_schemas = dict()
        self.components = Components()
        self.tags = []
        self.tag_names = []
        self.doc_prefix = doc_prefix
        self.api_doc_url = api_doc_url
        self.swagger_url = swagger_url
        self.redoc_url = redoc_url
        self.rapidoc_url = rapidoc_url
        if oauth_config:
            if not isinstance(oauth_config, OAuthConfig):
                raise TypeError("`initOAuth` must be `OAuthConfig`")
        self.oauth_config = oauth_config
        if doc_ui:
            self.init_doc()
        self.doc_expansion = doc_expansion
        self.severs = servers
        self.external_docs = external_docs
        # add openapi command
        self.cli.add_command(openapi_command)

    def init_doc(self) -> None:
        """
        Provide Swagger UI, Redoc and Rapidoc
        """
        _here = os.path.dirname(__file__)
        template_folder = os.path.join(_here, "templates")
        static_folder = os.path.join(template_folder, "static")

        blueprint = Blueprint(
            "openapi",
            __name__,
            url_prefix=self.doc_prefix,
            template_folder=template_folder,
            static_folder=static_folder
        )
        blueprint.add_url_rule(
            rule=self.api_doc_url,
            endpoint="api_doc",
            view_func=lambda: self.api_doc
        )
        blueprint.add_url_rule(
            rule=self.swagger_url,
            endpoint="swagger",
            view_func=lambda: render_template(
                "swagger.html",
                api_doc_url=self.api_doc_url.lstrip("/"),
                doc_expansion=self.doc_expansion,
                oauth_config=self.oauth_config.dict() if self.oauth_config else None
            )
        )
        blueprint.add_url_rule(
            rule=self.redoc_url,
            endpoint="redoc",
            view_func=lambda: render_template(
                "redoc.html",
                api_doc_url=self.api_doc_url.lstrip("/")
            )
        )
        blueprint.add_url_rule(
            rule=self.rapidoc_url,
            endpoint="rapidoc",
            view_func=lambda: render_template(
                "rapidoc.html",
                api_doc_url=self.api_doc_url.lstrip("/")
            )
        )
        blueprint.add_url_rule(
            rule="/",
            endpoint="index",
            view_func=lambda: render_template(
                "index.html",
                swagger_url=self.swagger_url.lstrip("/"),
                redoc_url=self.redoc_url.lstrip("/"),
                rapidoc_url=self.rapidoc_url.lstrip("/")
            )
        )
        self.register_blueprint(blueprint)

    @property
    def api_doc(self) -> Dict:
        """Generate Specification json"""
        spec = APISpec(
            openapi=self.openapi_version,
            info=self.info,
            servers=self.severs,
            externalDocs=self.external_docs
        )
        spec.tags = self.tags or None
        spec.paths = self.paths
        self.components.schemas = self.components_schemas
        self.components.securitySchemes = self.security_schemes
        spec.components = self.components
        return json.loads(spec.json(by_alias=True, exclude_none=True))

    def register_api(self, api: APIBlueprint) -> None:
        """Register APIBlueprint"""
        for tag in api.tags:
            if tag.name not in self.tag_names:
                self.tags.append(tag)
        self.paths.update(**api.paths)
        self.components_schemas.update(**api.components_schemas)
        self.register_blueprint(api)

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
        """
        Collect openapi specification information
        :param rule: Flask route
        :param func: Flask view_func
        :param tags: API tag
        :param responses: Response model
        :param extra_responses: Extra response dict
        :param security: Security name
        :param deprecated: Mark as deprecated support. Default to not True.
        :param doc_ui: Add openapi document UI(swagger, rapidoc and redoc). Defaults to True.
        :param operation_id: Unique string used to identify the operation.
        :param method: API method
        :return:
        """
        if doc_ui is True:
            if responses is None:
                responses = {}
            if extra_responses is None:
                extra_responses = {}
            validate_responses_type(responses)
            validate_responses_type(self.responses)
            validate_responses_type(extra_responses)
            # global response combine api responses
            combine_responses = deepcopy(self.responses)
            combine_responses.update(**responses)
            # create operation
            operation = get_operation(func, summary=summary, description=description)
            # set external docs
            operation.externalDocs = external_docs
            # Unique string used to identify the operation.
            if operation_id:
                operation.operationId = operation_id
            else:
                operation.operationId = get_operation_id_for_path(name=func.__name__, path=rule, method=method)
            # only set `deprecated` if True otherwise leave it as None
            operation.deprecated = deprecated
            # add security
            operation.security = security
            # add servers
            operation.servers = servers
            # store tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)
            # parse parameters
            header, cookie, path, query, form, body = parse_parameters(
                func,
                extra_form=extra_form,
                extra_body=extra_body,
                components_schemas=self.components_schemas,
                operation=operation
            )
            # parse response
            get_responses(combine_responses, extra_responses, self.components_schemas, operation)
            # /pet/<petId> --> /pet/{petId}
            uri = re.sub(r"<([^<:]+:)?", "{", rule).replace(">", "}")
            # parse method
            parse_method(uri, method, self.paths, operation)
            return header, cookie, path, query, form, body
        else:
            # parse parameters
            header, cookie, path, query, form, body = parse_parameters(func, doc_ui=False)
            return header, cookie, path, query, form, body

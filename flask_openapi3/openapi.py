# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:25
import json
import os
from copy import deepcopy
from functools import wraps
from io import StringIO
from typing import Optional, List, Dict, Union, Any, Type, Callable, Tuple

from flask import Flask, Blueprint, render_template, request, make_response, current_app
from flask.wrappers import Response
from pydantic import ValidationError, BaseModel
from werkzeug.datastructures import MultiDict

from .http import HTTPMethod
from .markdown import openapi_to_markdown
from .models import Info, APISpec, Tag, Components, Server
from .models.common import Reference, ExternalDocumentation
from .models.oauth import OAuthConfig
from .models.security import SecurityScheme
from .utils import get_openapi_path, get_operation, get_responses, parse_and_store_tags, parse_parameters, \
    validate_responses_type, parse_method, validate_response


def _do_wrapper(
        func: Callable,
        *,
        responses: Dict[str, Type[BaseModel]] = None,
        header: Type[BaseModel] = None,
        cookie: Type[BaseModel] = None,
        path: Type[BaseModel] = None,
        query: Type[BaseModel] = None,
        form: Type[BaseModel] = None,
        body: Type[BaseModel] = None,
        **kwargs: Any
) -> Response:
    """
    Validate requests and responses
    :param func: view func
    :param responses: response model
    :param header: header model
    :param cookie: cookie model
    :param path: path model
    :param query: query model
    :param form: form model
    :param body: body model
    :param kwargs: path parameters
    :return:
    """
    # validate header, cookie, path and query
    kwargs_ = dict()
    try:
        if header:
            request_headers = dict(request.headers) if request.headers is not None else {}
            for key, value in header.__annotations__.items():
                ket_title = key.title()
                # add original key
                if ket_title in request_headers.keys():
                    request_headers[key] = request_headers[ket_title]
            header_ = header(**request_headers)
            kwargs_.update({"header": header_})
        if cookie:
            cookie_ = cookie(**request.cookies if request.cookies is not None else {})
            kwargs_.update({"cookie": cookie_})
        if path:
            path_ = path(**kwargs)
            kwargs_.update({"path": path_})
        if query:
            args = request.args or MultiDict()
            args_dict = {}
            for k, v in query.schema().get('properties', {}).items():
                if v.get('type') == 'array':
                    value = args.getlist(k)
                else:
                    value = args.get(k)
                if value is not None:
                    args_dict[k] = value
            query_ = query(**args_dict)
            kwargs_.update({"query": query_})
        if form:
            req_form = request.form or MultiDict()
            form_dict = {}
            for k, v in form.schema().get('properties', {}).items():
                if v.get('type') == 'array':
                    value = req_form.getlist(k)
                else:
                    value = req_form.get(k)
                if value is not None:
                    form_dict[k] = value
            form_dict.update(**request.files.to_dict())
            form_ = form(**form_dict)
            kwargs_.update({"form": form_})
        if body:
            body_ = body(
                **request.get_json(silent=True) if request.get_json(silent=True) is not None else {})
            kwargs_.update({"body": body_})
    except ValidationError as e:
        resp = make_response(e.json())
        resp.headers['Content-Type'] = 'application/json'
        resp.status_code = 422
        return resp

    # handle request
    resp = func(**kwargs_)

    validate_resp = current_app.config.get("VALIDATE_RESPONSE", False)
    if validate_resp and responses:
        validate_response(resp, responses)

    return resp


class APIBlueprint(Blueprint):
    def __init__(
            self,
            name: str,
            import_name: str,
            *,
            abp_tags: Optional[List[Tag]] = None,
            abp_security: Optional[List[Dict[str, List[str]]]] = None,
            abp_responses: Optional[Dict[str, Type[BaseModel]]] = None,
            doc_ui: bool = True,
            **kwargs: Any
    ) -> None:
        """
        Based on Flask Blueprint

        Arguments:
            name: The name of the blueprint. Will be prepended to each endpoint name.
            import_name: The name of the blueprint package, usually
                         ``__name__``. This helps locate the ``root_path`` for the blueprint.
            abp_tags: APIBlueprint tags for every api
            abp_security: APIBlueprint security for every api
            abp_responses: APIBlueprint response model
            doc_ui: add openapi document UI(swagger and redoc). Defaults to True.
            kwargs: Flask Blueprint kwargs
        """
        super(APIBlueprint, self).__init__(name, import_name, **kwargs)
        self.paths = dict()
        self.components_schemas = dict()
        self.components = Components()
        self.tags = []
        self.tag_names = []

        self.abp_tags = abp_tags or []
        self.abp_security = abp_security or []
        self.abp_responses = abp_responses or {}
        self.doc_ui = doc_ui

    def _do_decorator(
            self,
            rule: str,
            func: Callable,
            *,
            tags: List[Tag] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            extra_responses: Dict[str, dict] = None,
            security: List[Dict[str, List[Any]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> Tuple[
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Dict[str, Type[BaseModel]]
    ]:
        """
        Collect openapi specification information
        :param rule: flask route
        :param func: flask view_func
        :param tags: api tag
        :param responses: response model
        :param extra_responses: extra response's dict
        :param security: security name
        :param doc_ui: add openapi document UI(swagger and redoc). Defaults to True.
        :param deprecated: mark as deprecated support. Default to not True.
        :param method: api method
        :return:
        """
        if self.doc_ui is True and doc_ui is True:
            if responses is None:
                responses = {}
            if extra_responses is None:
                extra_responses = {}
            validate_responses_type(responses)
            validate_responses_type(self.abp_responses)
            validate_responses_type(extra_responses)
            # global response combine api responses
            combine_responses = deepcopy(self.abp_responses)
            combine_responses.update(**responses)
            # create operation
            operation = get_operation(func, summary=summary, description=description)
            # add security
            if security is None:
                security = []
            operation.security = security + self.abp_security or None
            # only set `deprecated` if True otherwise leave it as None
            if deprecated:
                operation.deprecated = True
            # store tags
            tags = tags + self.abp_tags if tags else self.abp_tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)
            # parse parameters
            header, cookie, path, query, form, body = \
                parse_parameters(func, components_schemas=self.components_schemas, operation=operation)
            # parse response
            get_responses(combine_responses, extra_responses, self.components_schemas, operation)
            uri = get_openapi_path(rule)
            # merge url_prefix and uri
            uri = self.url_prefix.rstrip("/") + "/" + uri.lstrip("/") if self.url_prefix else uri
            # strip the right slash
            uri = uri.rstrip('/')
            # parse method
            parse_method(uri, method, self.paths, operation)
            return header, cookie, path, query, form, body, combine_responses
        else:
            # parse parameters
            header, cookie, path, query, form, body = parse_parameters(func, doc_ui=False)
            return header, cookie, path, query, form, body, {}

    def get(
            self,
            rule: str,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['GET'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.GET
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.GET]}
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
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['POST'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.POST
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.POST]}
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
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['PUT'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PUT
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.PUT]}
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
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['DELETE'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.DELETE
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.DELETE]}
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
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['PATCH'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PATCH
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.PATCH]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator


class OpenAPI(Flask):
    def __init__(
            self,
            import_name: str,
            *,
            info: Optional[Info] = None,
            security_schemes: Optional[Dict[str, Union[SecurityScheme, Reference]]] = None,
            oauth_config: Optional[OAuthConfig] = None,
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            doc_ui: bool = True,
            doc_expansion: str = "list",
            servers: Optional[List[Server]] = None,
            **kwargs: Any
    ) -> None:
        """
        Based on Flask. Provide REST api, swagger-ui and redoc.

        Arguments:
            import_name: just flask import_name
            info: see https://spec.openapis.org/oas/v3.0.3#info-object
            security_schemes: see https://spec.openapis.org/oas/v3.0.3#security-scheme-object
            oauth_config: OAuth 2.0 configuration,
                          see https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md
            responses: OpenAPI response model
            doc_ui: add openapi document UI(swagger and redoc). Defaults to True.
            doc_expansion: String=["list"*, "full", "none"].
                          Controls the default expansion setting for the operations and tags.
                          It can be 'list' (expands only the tags),
                         'full' (expands the tags and operations) or 'none' (expands nothing).
                         see https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/configuration.md
            servers: An array of Server Objects, which provide connectivity information to a target server.
            kwargs: Flask kwargs
        """
        super(OpenAPI, self).__init__(import_name, **kwargs)

        self.openapi_version = "3.0.3"
        if info is None:
            info = Info(title='OpenAPI', version='1.0.0')
        assert isinstance(info, Info), f"Info is required (got type {type(info)})"
        self.info = info
        self.security_schemes = security_schemes
        self.responses = responses or {}
        self.paths = dict()
        self.components_schemas = dict()
        self.components = Components()
        self.tags = []
        self.tag_names = []
        self.api_name = 'openapi'
        self.api_doc_url = f"/{self.api_name}.json"
        if oauth_config:
            if not isinstance(oauth_config, OAuthConfig):
                raise TypeError("`initOAuth` must be `OAuthConfig`")
        self.oauth_config = oauth_config
        if doc_ui:
            self.init_doc()
        self.doc_expansion = doc_expansion
        self.severs = servers

    def init_doc(self) -> None:
        """
        Provide swagger-ui and redoc
        """
        _here = os.path.dirname(__file__)
        template_folder = os.path.join(_here, 'templates')
        static_folder = os.path.join(template_folder, 'static')

        blueprint = Blueprint(
            self.api_name,
            __name__,
            url_prefix=f'/{self.api_name}',
            template_folder=template_folder,
            static_folder=static_folder
        )
        blueprint.add_url_rule(
            rule=self.api_doc_url,
            endpoint=self.api_name,
            view_func=lambda: self.api_doc
        )
        blueprint.add_url_rule(
            rule='/swagger',
            endpoint='swagger',
            view_func=lambda: render_template(
                "swagger.html",
                api_doc_url=f'{self.api_name}.json',
                doc_expansion=self.doc_expansion,
                oauth_config=self.oauth_config.dict() if self.oauth_config else None
            )
        )
        blueprint.add_url_rule(
            rule='/redoc',
            endpoint='redoc',
            view_func=lambda: render_template(
                "redoc.html",
                api_doc_url=f'{self.api_name}.json'
            )
        )
        blueprint.add_url_rule(
            rule='/rapidoc',
            endpoint='rapidoc',
            view_func=lambda: render_template(
                "rapidoc.html",
                api_doc_url=f'{self.api_name}.json'
            )
        )
        blueprint.add_url_rule(
            rule='/markdown',
            endpoint='markdown',
            view_func=lambda: self.export_to_markdown()
        )
        blueprint.add_url_rule(
            rule='/',
            endpoint='index',
            view_func=lambda: render_template("index.html")
        )
        self.register_blueprint(blueprint)

    def export_to_markdown(self) -> Response:
        """Experimental"""
        md = StringIO()

        md.write(openapi_to_markdown(self.api_doc))

        r = make_response(md.getvalue())
        r.headers['Content-Disposition'] = 'attachment; filename=api.md'

        return r

    @property
    def api_doc(self) -> Dict:
        """Generate spec json"""
        spec = APISpec(
            openapi=self.openapi_version,
            info=self.info,
            servers=self.severs,
            externalDocs=ExternalDocumentation(
                url=f'/{self.api_name}/markdown',
                description='Export to markdown'
            )
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
            responses: Dict[str, Type[BaseModel]] = None,
            extra_responses: Dict[str, dict] = None,
            security: List[Dict[str, List[Any]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True,
            method: str = HTTPMethod.GET
    ) -> Tuple[
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Type[BaseModel],
        Dict[str, Type[BaseModel]]
    ]:
        """
        Collect openapi specification information
        :param rule: flask route
        :param func: flask view_func
        :param tags: api tag
        :param responses: response model
        :param extra_responses: extra responses dict
        :param security: security name
        :param deprecated: mark as deprecated support. Default to not True.
        :param doc_ui: add openapi document UI(swagger and redoc). Defaults to True.
        :param method: api method
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
            # add security
            operation.security = security
            # only set `deprecated` if True otherwise leave it as None
            if deprecated:
                operation.deprecated = True
            # store tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)
            # parse parameters
            header, cookie, path, query, form, body = \
                parse_parameters(func, components_schemas=self.components_schemas, operation=operation)
            # parse response
            get_responses(combine_responses, extra_responses, self.components_schemas, operation)
            uri = get_openapi_path(rule)
            # parse method
            parse_method(uri, method, self.paths, operation)
            return header, cookie, path, query, form, body, combine_responses
        else:
            # parse parameters
            header, cookie, path, query, form, body = parse_parameters(func, doc_ui=False)
            return header, cookie, path, query, form, body, {}

    def get(
            self,
            rule: str,
            *,
            tags: Optional[List[Tag]] = None,
            summary: Optional[str] = None,
            description: Optional[str] = None,
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['GET'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.GET
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.GET]}
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
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['POST'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.POST
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.POST]}
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
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['PUT'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PUT
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.PUT]}
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
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['DELETE'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.DELETE
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.DELETE]}
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
            responses: Optional[Dict[str, Type[BaseModel]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            deprecated: Optional[bool] = None,
            doc_ui: bool = True
    ) -> Callable:
        """Decorator for rest api, like: app.route(methods=['PATCH'])"""

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body, combine_responses = \
                self._do_decorator(
                    rule,
                    func,
                    tags=tags,
                    summary=summary,
                    description=description,
                    responses=responses,
                    extra_responses=extra_responses,
                    security=security,
                    deprecated=deprecated,
                    doc_ui=doc_ui,
                    method=HTTPMethod.PATCH
                )

            @wraps(func)
            def wrapper(**kwargs) -> Response:
                resp = _do_wrapper(
                    func,
                    responses=combine_responses,
                    header=header,
                    cookie=cookie,
                    path=path,
                    query=query,
                    form=form,
                    body=body,
                    **kwargs
                )
                return resp

            options = {"methods": [HTTPMethod.PATCH]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

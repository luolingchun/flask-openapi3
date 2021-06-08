# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/4/30 14:25
import json
import os
from functools import wraps
from typing import Optional, List, Dict, Union, Any, Type, Callable, Tuple

from flask import Flask, Blueprint, render_template, request, make_response
from pydantic import ValidationError, BaseModel

from .models import Info, APISpec, Tag, Components
from .models.common import Reference
from .models.security import SecurityScheme
from .utils import _parse_rule, get_operation, get_responses, parse_and_store_tags, parse_parameters, \
    validate_responses, parse_method, validate_response


def _do_wrapper(
        func: Callable,
        responses: Dict[str, Type[BaseModel]] = None,
        header: Type[BaseModel] = None,
        cookie: Type[BaseModel] = None,
        path: Type[BaseModel] = None,
        query: Type[BaseModel] = None,
        form: Type[BaseModel] = None,
        body: Type[BaseModel] = None,
        validate_resp: bool = None,
        **kwargs: Any
) -> Any:
    """
    validate request and response
    :param func: view func
    :param responses: response model
    :param header:
    :param cookie:
    :param path:
    :param query:
    :param form:
    :param body:
    :param validate_resp: boolean, is validate response
    :param kwargs: path args
    :return:
    """
    validate_responses(responses)
    # validate header, cookie, path and query
    kwargs_ = dict()
    try:
        if header:
            header_ = header(**request.headers if request.headers is not None else {})
            kwargs_.update({"header": header_})
        if cookie:
            cookie_ = cookie(**request.cookies if request.cookies is not None else {})
            kwargs_.update({"cookie": cookie_})
        if path:
            path_ = path(**kwargs)
            kwargs_.update({"path": path_})
        if query:
            query_ = query(**request.args.to_dict() if request.args.to_dict() is not None else {})
            kwargs_.update({"query": query_})
        if form:
            req_form = request.form.to_dict()
            req_form.update(**request.files.to_dict() if request.files.to_dict() is not None else {})
            form_ = form(**req_form if req_form is not None else {})
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
    if validate_resp:
        validate_response(resp, responses)

    return resp


class APIBlueprint(Blueprint):
    def __init__(
            self,
            name: str,
            import_name: str,
            abp_tags: List[Tag] = None,
            abp_security: List[Dict[str, List[str]]] = None,
            **kwargs: Any
    ):
        """
        Based on Flask Blueprint
        :param args: Flask Blueprint args
        :param abp_tags: APIBlueprint tags for every api
        :param abp_security: APIBlueprint security for every api
        :param kwargs: Flask Blueprint kwargs
        """
        super(APIBlueprint, self).__init__(name, import_name, **kwargs)
        self.paths = dict()
        self.components_schemas = dict()
        self.components = Components()
        self.tags = []
        self.tag_names = []

        self.abp_tags = abp_tags
        if self.abp_tags is None:
            self.abp_tags = []

        self.abp_security = abp_security
        if self.abp_security is None:
            self.abp_security = []

    def _do_decorator(
            self,
            rule: str,
            func: Callable,
            tags: List[Tag] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            security: List[Dict[str, List[Any]]] = None,
            method: str = 'get'
    ) -> Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel]]:
        """
        collect openapi spec information
        :param rule: flask route
        :param func: flask view_func
        :param tags: api tag
        :param responses: response model
        :param security: security name
        :param method: api method
        :return:
        """
        validate_responses(responses)
        # create operation
        operation = get_operation(func)
        # add security
        if security is None:
            security = []
        operation.security = security + self.abp_security or None
        # store tags
        tags = tags + self.abp_tags if tags else self.abp_tags
        parse_and_store_tags(tags, self.tags, self.tag_names, operation)
        # parse parameters
        header, cookie, path, query, form, body = parse_parameters(func, self.components_schemas, operation)
        # parse response
        get_responses(responses, self.components_schemas, operation)
        uri = _parse_rule(rule)
        # merge url_prefix and uri
        uri = self.url_prefix.rstrip("/") + "/" + uri.lstrip("/") if self.url_prefix else uri
        # strip the right slash
        uri = uri.rstrip('/')
        # parse method
        parse_method(uri, method, self.paths, operation)
        return header, cookie, path, query, form, body

    def get(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ):
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security)

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["GET"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def post(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ):
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security, "post")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["POST"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def put(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ):
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security, "put")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["PUT"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def delete(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ):
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security,
                                                                         "delete")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["DELETE"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def patch(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ):
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security, "patch")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["PATCH"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator


class OpenAPI(Flask):
    def __init__(self,
                 import_name: str,
                 info: Info = None,
                 securitySchemes: Optional[Dict[str, Union[SecurityScheme, Reference]]] = None,
                 doc_ui: bool = True,
                 **kwargs: Any
                 ) -> None:
        """
        Based Flask, provide REST api, swagger-ui and redoc.
        :param import_name: just flask import_name
        :param info: see https://spec.openapis.org/oas/v3.0.3#info-object
        :param securitySchemes: see https://spec.openapis.org/oas/v3.0.3#security-scheme-object
        :param doc_ui: add openapi document UI(swagger and redoc). Defaults to True.
        :param kwargs:
        """
        super(OpenAPI, self).__init__(import_name, **kwargs)

        self.openapi_version = "3.0.3"
        if info is None:
            info = Info(title='OpenAPI', version='1.0.0')
        assert isinstance(info, Info), f"Info is required (got type {type(info)})"
        self.info = info
        self.securitySchemes = securitySchemes
        self.paths = dict()
        self.components_schemas = dict()
        self.components = Components()
        self.tags = []
        self.tag_names = []
        self.api_name = 'openapi'
        self.api_doc_url = f"/{self.api_name}.json"
        if doc_ui:
            self.init_doc()

    def init_doc(self) -> None:
        """
        provide swagger-ui and redoc
        :return:
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
        blueprint.add_url_rule(rule=self.api_doc_url, endpoint=self.api_name, view_func=lambda: self.api_doc)
        blueprint.add_url_rule(rule='/redoc', endpoint='redoc',
                               view_func=lambda: render_template("redoc.html", api_doc_url=f'{self.api_name}.json'))
        blueprint.add_url_rule(rule='/swagger', endpoint='swagger',
                               view_func=lambda: render_template("swagger.html", api_doc_url=f'{self.api_name}.json'))
        blueprint.add_url_rule(rule='/', endpoint='index',
                               view_func=lambda: render_template("index.html"))
        self.register_blueprint(blueprint)

    @property
    def api_doc(self) -> Dict:
        """generate spec json"""
        spec = APISpec(openapi=self.openapi_version, info=self.info)
        spec.tags = self.tags or None
        spec.paths = self.paths
        self.components.schemas = self.components_schemas
        self.components.securitySchemes = self.securitySchemes
        spec.components = self.components
        return json.loads(spec.json(by_alias=True, exclude_none=True))

    def register_api(self, api: APIBlueprint) -> None:
        """register APIBlueprint"""
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
            tags: List[Tag] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            security: List[Dict[str, List[Any]]] = None,
            method: str = 'get'
    ) -> Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel]]:
        """
        collect openapi spec information
        :param rule: flask route
        :param func: flask view_func
        :param tags: api tag
        :param responses: response model
        :param security: security name
        :param method: api method
        :return:
        """
        validate_responses(responses)
        # create operation
        operation = get_operation(func)
        # add security
        operation.security = security
        # store tags
        parse_and_store_tags(tags, self.tags, self.tag_names, operation)
        # parse parameters
        header, cookie, path, query, form, body = parse_parameters(func, self.components_schemas, operation)
        # parse response
        get_responses(responses, self.components_schemas, operation)
        uri = _parse_rule(rule)
        # parse method
        parse_method(uri, method, self.paths, operation)
        return header, cookie, path, query, form, body

    def get(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ) -> Callable:
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security)

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["GET"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def post(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ) -> Callable:
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security, "post")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["POST"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def put(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ) -> Callable:
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security, "put")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["PUT"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def delete(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ) -> Callable:
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security,
                                                                         "delete")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["DELETE"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

    def patch(
            self,
            rule: str,
            tags: Optional[List[Tag]] = None,
            responses: Dict[str, Type[BaseModel]] = None,
            validate_resp: bool = True,
            security: List[Dict[str, List[Any]]] = None
    ) -> Callable:
        def decorator(func):
            header, cookie, path, query, form, body = self._do_decorator(rule, func, tags, responses, security, "patch")

            @wraps(func)
            def wrapper(**kwargs):
                resp = _do_wrapper(func, responses, header, cookie, path, query, form, body, validate_resp, **kwargs)
                return resp

            options = {"methods": ["PATCH"]}
            self.add_url_rule(rule, view_func=wrapper, **options)

            return wrapper

        return decorator

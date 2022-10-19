# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2022/10/14 16:09
from typing import Optional, List, Dict, Type, Any, Callable
from uuid import uuid4

from flask.views import MethodView
from pydantic import BaseModel

from .models.common import ExternalDocumentation, ExtraRequestBody
from .models.server import Server
from .models.tag import Tag


class APIView:
    def __init__(
            self,
            url_prefix: Optional[str] = None,
            view_tags: Optional[List[Tag]] = None,
            view_security: Optional[List[Dict[str, List[str]]]] = None,
            view_responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            doc_ui: bool = True
    ):
        self.url_prefix = url_prefix
        self.view_tags = view_tags
        self.view_security = view_security
        self.view_responses = view_responses
        self.doc_ui = doc_ui

        self.method_view_dict = {}

    def route(self, rule: str):
        def wrapper(cls):
            _dict = {'__doc__': cls.__doc__}
            for method in ["get", "post", "put", "patch", "delete"]:
                if hasattr(cls, method):
                    _dict[method] = getattr(cls, method)
            # Inherit from MethodView
            method_view = type(f"{cls.__name__}-{uuid4()}", (MethodView,), _dict)
            if self.url_prefix:
                _rule = self.url_prefix.rstrip("/") + "/" + rule.lstrip("/")
            else:
                _rule = rule
            if self.method_view_dict.get(_rule):
                raise ValueError(f"malformed url rule: {_rule!r}")
            self.method_view_dict[_rule] = method_view
            return cls

        return wrapper

    def doc(
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
            responses: Optional[Dict[str, Optional[Type[BaseModel]]]] = None,
            extra_responses: Optional[Dict[str, dict]] = None,
            deprecated: Optional[bool] = None,
            security: Optional[List[Dict[str, List[Any]]]] = None,
            servers: Optional[List[Server]] = None,
            doc_ui: bool = True,
            **options: Any
    ) -> Callable:
        """
        Decorator for rest api, like: app.route(methods=["POST"])
        More information goto https://spec.openapis.org/oas/v3.0.3#operation-object

        Arguments:
            rule: The URL rule string.
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

        raise NotImplementedError()


if __name__ == "__main__":
    api_view = APIView()

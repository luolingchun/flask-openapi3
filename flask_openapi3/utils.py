# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/1 21:34

import inspect
import re
from http import HTTPStatus
from typing import get_type_hints, Dict, Type, Callable, List, Tuple, Optional, Any

from flask import make_response, current_app
from flask.wrappers import Response as FlaskResponse
from pydantic import BaseModel, ValidationError

from ._http import HTTP_STATUS, HTTPMethod
from .models import Encoding
from .models import ExtraRequestBody
from .models import MediaType
from .models import OPENAPI3_REF_PREFIX
from .models import OPENAPI3_REF_TEMPLATE
from .models import Operation
from .models import Parameter
from .models import ParameterInType
from .models import PathItem
from .models import RequestBody
from .models import Response
from .models import Schema
from .models import Tag
from .types import ParametersTuple
from .types import ResponseDict
from .types import ResponseStrKeyDict


def get_operation(
        func: Callable, *,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        openapi_extensions: Optional[Dict[str, Any]] = None,
) -> Operation:
    """
    Return an Operation object with the specified summary and description.

    Arguments:
        func: The function or method for which the operation is being defined.
        summary: A short summary of what the operation does.
        description: A verbose explanation of the operation behavior.
        openapi_extensions: Additional extensions to the OpenAPI Schema.

    Returns:
        An Operation object representing the operation.

    """
    # Get the docstring of the function
    doc = inspect.getdoc(func) or ""
    doc = doc.strip()
    lines = doc.split("\n")
    doc_summary = lines[0] or None

    # Determine the summary and description based on provided arguments or docstring
    if summary is None:
        doc_description = lines[0] if len(lines) == 0 else "</br>".join(lines[1:]) or None
    else:
        doc_description = "</br>".join(lines) or None

    # Create the operation dictionary with summary and description
    operation_dict = dict(
        summary=summary or doc_summary,
        description=description or doc_description
    )

    # Add any additional openapi_extensions to the operation dictionary
    openapi_extensions = openapi_extensions or {}
    operation_dict.update(**openapi_extensions)

    # Create and return the Operation object
    operation = Operation(**operation_dict)

    return operation


def get_operation_id_for_path(*, name: str, path: str, method: str) -> str:
    """
    Generate a unique operation ID based on the name, path, and method.

    Arguments:
        name: The name or identifier for the operation.
        path: The URL path for the operation.
        method: The HTTP method for the operation.

    Returns:
        A unique operation ID generated based on the provided name, path, and method.

    """
    operation_id = name + path
    # Replace non-word characters with underscores
    operation_id = re.sub(r"\W", "_", operation_id)
    operation_id = operation_id + "_" + method.lower()
    return operation_id


def get_model_schema(model: Type[BaseModel]) -> dict:
    """Converts a Pydantic model to an OpenAPI schema."""

    assert inspect.isclass(model) and issubclass(model, BaseModel), \
        f"{model} is invalid `pydantic.BaseModel`"

    model_config = model.Config
    by_alias = getattr(model_config, "by_alias", True)

    return model.schema(by_alias=by_alias, ref_template=OPENAPI3_REF_TEMPLATE)


def parse_header(header: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parses a header model and returns a list of parameters and component schemas."""
    schema = get_model_schema(header)
    parameters = []
    components_schemas: Dict = dict()
    properties = schema.get("properties", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.HEADER,
            "description": value.get("description"),
            "required": name in schema.get("required", []),
            "schema": Schema(**value)
        }
        # Parse extra values
        data.update({
            "deprecated": value.get("deprecated"),
            "example": value.get("example"),
            "examples": value.get("examples"),
        })
        parameters.append(Parameter(**data))

    # Parse definitions
    definitions = schema.get("definitions", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_cookie(cookie: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parses a cookie model and returns a list of parameters and component schemas."""
    schema = get_model_schema(cookie)
    parameters = []
    components_schemas: Dict = dict()
    properties = schema.get("properties", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.COOKIE,
            "description": value.get("description"),
            "required": name in schema.get("required", []),
            "schema": Schema(**value)
        }
        # Parse extra values
        data.update({
            "deprecated": value.get("deprecated"),
            "example": value.get("example"),
            "examples": value.get("examples"),
        })
        parameters.append(Parameter(**data))

    # Parse definitions
    definitions = schema.get("definitions", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_path(path: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parses a path model and returns a list of parameters and component schemas."""
    schema = get_model_schema(path)
    parameters = []
    components_schemas: Dict = dict()
    properties = schema.get("properties", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.PATH,
            "description": value.get("description"),
            "required": True,
            "schema": Schema(**value)
        }
        # Parse extra values
        data.update({
            "deprecated": value.get("deprecated"),
            "example": value.get("example"),
            "examples": value.get("examples"),
        })
        parameters.append(Parameter(**data))

    # Parse definitions
    definitions = schema.get("definitions", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_query(query: Type[BaseModel]) -> Tuple[List[Parameter], dict]:
    """Parses a query model and returns a list of parameters and component schemas."""
    schema = get_model_schema(query)
    parameters = []
    components_schemas: Dict = dict()
    properties = schema.get("properties", {})

    for name, value in properties.items():
        data = {
            "name": name,
            "in": ParameterInType.QUERY,
            "description": value.get("description"),
            "required": name in schema.get("required", []),
            "schema": Schema(**value)
        }
        # Parse extra values
        data.update({
            "deprecated": value.get("deprecated"),
            "example": value.get("example"),
            "examples": value.get("examples"),
        })
        parameters.append(Parameter(**data))

    # Parse definitions
    definitions = schema.get("definitions", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return parameters, components_schemas


def parse_form(
        form: Type[BaseModel],
        extra_form: Optional[ExtraRequestBody] = None,
) -> Tuple[Dict[str, MediaType], dict]:
    """Parses a form model and returns a list of parameters and component schemas."""
    schema = get_model_schema(form)
    components_schemas = dict()
    properties = schema.get("properties", {})

    assert properties, f"{form.__name__}'s properties cannot be empty."

    original_title = schema.get("title") or form.__name__
    title = normalize_name(original_title)
    components_schemas[title] = Schema(**schema)
    encoding = {}
    for k, v in properties.items():
        if v.get("type") == "array":
            encoding[k] = Encoding(style="form", explode=True)
    if extra_form:
        # Update encoding
        if extra_form.encoding:
            encoding.update(**extra_form.encoding)
        content = {
            "multipart/form-data": MediaType(
                schema=Schema(**{"$ref": f"{OPENAPI3_REF_PREFIX}/{title}"}),
                example=extra_form.example,
                examples=extra_form.examples,
                encoding=encoding or None
            )
        }
    else:
        content = {
            "multipart/form-data": MediaType(
                schema=Schema(**{"$ref": f"{OPENAPI3_REF_PREFIX}/{title}"}),
                encoding=encoding or None
            )
        }

    # Parse definitions
    definitions = schema.get("definitions", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return content, components_schemas


def parse_body(
        body: Type[BaseModel],
        extra_body: Optional[ExtraRequestBody] = None,
) -> Tuple[Dict[str, MediaType], dict]:
    """Parses a body model and returns a list of parameters and component schemas."""
    schema = get_model_schema(body)
    components_schemas = dict()

    original_title = schema.get("title") or body.__name__
    title = normalize_name(original_title)
    components_schemas[title] = Schema(**schema)
    if extra_body:
        content = {
            "application/json": MediaType(
                schema=Schema(**{"$ref": f"{OPENAPI3_REF_PREFIX}/{title}"}),
                example=extra_body.example,
                examples=extra_body.examples,
                encoding=extra_body.encoding
            )
        }
    else:
        content = {
            "application/json": MediaType(
                schema=Schema(**{"$ref": f"{OPENAPI3_REF_PREFIX}/{title}"})
            )
        }

    # Parse definitions
    definitions = schema.get("definitions", {})
    for name, value in definitions.items():
        components_schemas[name] = Schema(**value)

    return content, components_schemas


def get_responses(
        responses: ResponseStrKeyDict,
        extra_responses: Dict[str, dict],
        components_schemas: dict,
        operation: Operation
) -> None:
    _responses = {}
    _schemas = {}

    for key, response in responses.items():
        if response is None:
            # If the response is None, it means HTTP status code "204" (No Content)
            _responses[key] = Response(description=HTTP_STATUS.get(key, ""))
        elif isinstance(response, dict):
            if not response.get("description"):
                response["description"] = HTTP_STATUS.get(key, "")
            _responses[key] = Response(**response)
        else:
            # OpenAPI 3 support ^[a-zA-Z0-9\.\-_]+$ so we should normalize __name__
            name = normalize_name(response.__name__)
            schema = get_model_schema(response)
            _responses[key] = Response(
                description=HTTP_STATUS.get(key, ""),
                content={
                    "application/json": MediaType(
                        schema=Schema(**{"$ref": f"{OPENAPI3_REF_PREFIX}/{name}"})
                    )})

            model_config = response.Config
            openapi_extra = getattr(model_config, "openapi_extra", None)
            if openapi_extra is not None:
                # Add additional information from model_config to the response
                _responses[key].description = openapi_extra.get("description")
                _responses[key].headers = openapi_extra.get("headers")
                _responses[key].links = openapi_extra.get("links")
                _content = _responses[key].content
                if _content is not None:
                    _content["application/json"].example = openapi_extra.get("example")
                    _content["application/json"].examples = openapi_extra.get("examples")
                    _content["application/json"].encoding = openapi_extra.get("encoding")
                    _content.update(openapi_extra.get("content", {}))

            _schemas[name] = Schema(**schema)
            definitions = schema.get("definitions")
            if definitions:
                # Add schema definitions to _schemas
                for name, value in definitions.items():
                    _schemas[normalize_name(name)] = Schema(**value)

    # handle extra_responses
    for key, value in extra_responses.items():
        # key "200" value {"content":{"text/csv":{"schema":{"type": "string"}}}}
        new_response = Response(
            # Best effort to ensure there is always a description
            description=value.pop("description", HTTP_STATUS.get(key, "")),
            **value
        )
        _responses[key] = new_response.merge_with(_responses.get(key))

    components_schemas.update(**_schemas)
    operation.responses = _responses


def parse_and_store_tags(
        new_tags: List[Tag],
        old_tags: List[Tag],
        old_tag_names: List[str],
        operation: Operation
) -> None:
    """
    Parses new tags, stores them in an old_tags list if they are not already present,
    and updates the tags attribute of the operation object.

    Arguments:
        new_tags: A list of new Tag objects to be parsed and stored.
        old_tags: The list of existing Tag objects.
        old_tag_names: The list that names of existing tags.
        operation: The operation object whose tag attribute needs to be updated.

    Returns:
        None
    """
    # Iterate over each tag in new_tags
    for tag in new_tags:
        if tag.name not in old_tag_names:
            old_tag_names.append(tag.name)
            old_tags.append(tag)

    # Set the tags attribute of the operation object to a list of unique tag names from new_tags
    # If the resulting list is empty, set it to None
    operation.tags = list(set([tag.name for tag in new_tags])) or None


def parse_parameters(
        func: Callable,
        *,
        extra_form: Optional[ExtraRequestBody] = None,
        extra_body: Optional[ExtraRequestBody] = None,
        components_schemas: Optional[Dict] = None,
        operation: Optional[Operation] = None,
        doc_ui: bool = True,
) -> ParametersTuple:
    """
    Parses the parameters of a given function and returns the types for header, cookie, path,
    query, form, and body parameters. Also populates the Operation object with the parsed parameters.

    Arguments:
        func: The function to parse the parameters from.
        extra_form: Additional form data for the request body (default: None).
        extra_body: Additional body data for the request body (default: None).
        components_schemas: Dictionary to store the parsed components schemas (default: None).
        operation: Operation object to populate with parsed parameters (default: None).
        doc_ui: Flag indicating whether to return types for documentation UI (default: True).

    Returns:
        Tuple[Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel], Type[BaseModel]]:
        The types for header, cookie, path, query, form, and body parameters respectively.

    """
    # Get the type hints from the function
    annotations: Dict[str, Type[BaseModel]] = get_type_hints(func)

    # Get the types for header, cookie, path, query, form, and body parameters
    header = annotations.get("header")
    cookie = annotations.get("cookie")
    path = annotations.get("path")
    query = annotations.get("query")
    form = annotations.get("form")
    body = annotations.get("body")

    # If doc_ui is False, return the types without further processing
    if doc_ui is False:
        return header, cookie, path, query, form, body

    parameters = []

    # If components_schemas is None, initialize it as an empty dictionary
    if components_schemas is None:
        components_schemas = dict()

    # If operation is None, initialize it as an Operation object
    if operation is None:
        operation = Operation()

    if header:
        _parameters, _components_schemas = parse_header(header)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    if cookie:
        _parameters, _components_schemas = parse_cookie(cookie)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    if path:
        _parameters, _components_schemas = parse_path(path)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    if query:
        _parameters, _components_schemas = parse_query(query)
        parameters.extend(_parameters)
        components_schemas.update(**_components_schemas)

    if form:
        _content, _components_schemas = parse_form(form, extra_form)
        components_schemas.update(**_components_schemas)
        if extra_form:
            request_body = RequestBody(
                description=extra_form.description,
                content=_content,
                required=extra_form.required
            )
        else:
            request_body = RequestBody(content=_content)
        model_config = form.Config
        openapi_extra = getattr(model_config, "openapi_extra", None)
        if openapi_extra:
            request_body.description = openapi_extra.get("description")
            request_body.content["multipart/form-data"].example = openapi_extra.get("example")
            request_body.content["multipart/form-data"].examples = openapi_extra.get("examples")
            if openapi_extra.get("encoding"):
                request_body.content["multipart/form-data"].encoding = openapi_extra.get("encoding")
        operation.requestBody = request_body

    if body:
        _content, _components_schemas = parse_body(body, extra_body)
        components_schemas.update(**_components_schemas)
        if extra_body:
            request_body = RequestBody(
                description=extra_body.description,
                content=_content,
                required=extra_body.required
            )
        else:
            request_body = RequestBody(content=_content)
        model_config = body.Config
        openapi_extra = getattr(model_config, "openapi_extra", None)
        if openapi_extra:
            request_body.description = openapi_extra.get("description")
            request_body.required = openapi_extra.get("required", True)
            request_body.content["application/json"].example = openapi_extra.get("example")
            request_body.content["application/json"].examples = openapi_extra.get("examples")
            request_body.content["application/json"].encoding = openapi_extra.get("encoding")
        operation.requestBody = request_body

    # Set the parsed parameters in the operation object
    operation.parameters = parameters if parameters else None

    return header, cookie, path, query, form, body


def parse_method(uri: str, method: str, paths: dict, operation: Operation) -> None:
    """
    Parses the HTTP method and updates the corresponding PathItem object in the paths' dictionary.

    Arguments:
        uri: The URI of the API endpoint.
        method: The HTTP method for the API endpoint.
        paths: A dictionary containing the API paths and their corresponding PathItem objects.
        operation: The Operation object to assign to the PathItem.

    Returns:
        None
    """
    # Check the HTTP method and update the PathItem object in the path dictionary
    if method == HTTPMethod.GET:
        if not paths.get(uri):
            paths[uri] = PathItem(get=operation)
        else:
            paths[uri].get = operation
    elif method == HTTPMethod.POST:
        if not paths.get(uri):
            paths[uri] = PathItem(post=operation)
        else:
            paths[uri].post = operation
    elif method == HTTPMethod.PUT:
        if not paths.get(uri):
            paths[uri] = PathItem(put=operation)
        else:
            paths[uri].put = operation
    elif method == HTTPMethod.PATCH:
        if not paths.get(uri):
            paths[uri] = PathItem(patch=operation)
        else:
            paths[uri].patch = operation
    elif method == HTTPMethod.DELETE:
        if not paths.get(uri):
            paths[uri] = PathItem(delete=operation)
        else:
            paths[uri].delete = operation


def make_validation_error_response(e: ValidationError) -> FlaskResponse:
    """
    Create a Flask response for a validation error.

    Args:
        e: The ValidationError object containing the details of the error.

    Returns:
        FlaskResponse: A Flask Response object with the JSON representation of the error.
    """
    response = make_response(e.json())
    response.headers["Content-Type"] = "application/json"
    response.status_code = getattr(current_app, "validation_error_status", 422)
    return response


def parse_rule(rule: str, url_prefix=None) -> str:
    trail_slash = rule.endswith("/")

    # Merge url_prefix and uri
    uri = url_prefix.rstrip("/") + "/" + rule.lstrip("/") if url_prefix else rule

    if not trail_slash:
        uri = uri.rstrip("/")

    # Convert route parameter format from /pet/<petId> to /pet/{petId}
    uri = re.sub(r"<([^<:]+:)?", "{", uri).replace(">", "}")

    return uri


def convert_responses_key_to_string(responses: ResponseDict) -> ResponseStrKeyDict:
    """Convert key to string"""
    _responses = {}
    for key, value in responses.items():
        if isinstance(key, HTTPStatus):
            key = str(key.value)
        elif isinstance(key, int):
            key = str(key)
        _responses[key] = value

    return _responses


def normalize_name(name: str) -> str:
    return re.sub(r'[^\w.\-]', '_', name)

# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/8/11 10:39
from .models import OPENAPI3_REF_PREFIX


def parse_schemas(schemas):
    schemas_dict = {}
    for name, obj in schemas.items():
        schemas_dict[name] = "| name | type | required | description |\n"
        schemas_dict[name] += "| ---- | ---- | -------- | ----------- |\n"
        required = obj.get('required', [])
        enum = obj.get('enum')
        if enum:
            schemas_dict[name] += f"| {name} | {obj.get('type', '')} | - | Enum: {', '.join(enum)} |\n"
        properties = obj.get('properties')
        if properties:
            for property_name, _property in properties.items():
                ref = _property.get('$ref')
                if ref:
                    ref_name = ref.lstrip(OPENAPI3_REF_PREFIX + '/')
                    schemas_dict[name] += f"| {property_name} | - | - | [{ref_name}](#{ref_name}) |\n"
                else:
                    schemas_dict[name] += f"| {property_name} " \
                                          f"| {_property.get('format', '') or _property.get('type', '')} " \
                                          f"| {property_name in required} " \
                                          f"| {_property.get('description', '')} " \
                                          f"|\n"
    return schemas_dict


def parse_parameters(parameters):
    md = "| name | type | in   | required | description |\n"
    md += "| ---- | ---- | ---- | -------- | ----------- |\n"
    for param in parameters:
        aff_of = param['schema'].get('allOf')
        if aff_of:
            for one in aff_of:
                if isinstance(one, dict) and one.get('$ref'):
                    ref_name = one.get('$ref').lstrip(OPENAPI3_REF_PREFIX + '/')
                    md += f"| {param.get('name', '')} " \
                          f"| {param['schema'].get('type', '')} " \
                          f"| {param.get('in', '')} " \
                          f"| {param.get('required', '')} " \
                          f"| [{ref_name}](#{ref_name}) " \
                          f"|\n"
                    break
            continue
        md += f"| {param.get('name', '')} " \
              f"| {param['schema'].get('type', '')} " \
              f"| {param.get('in', '')} " \
              f"| {param.get('required', '')} " \
              f"| {param.get('description', '')} " \
              f"|\n"
    md += "\n"
    return md


def parse_request_body(request_body, schemas_dict):
    md = ''
    content = request_body['content']
    for media_type, schemas in content.items():
        md += f"*{media_type}*\n\n"
        ref = schemas['schema']['$ref']
        obj_name = ref.lstrip(OPENAPI3_REF_PREFIX + '/')
        md += f"{schemas_dict.get(obj_name, '')}"
    md += "\n"
    return md


def openapi_to_markdown(api_json: dict) -> str:
    markdown = ''
    # info and version
    info = api_json['info']
    markdown += f"# {info['title']}\n\n"
    markdown += f"**version**: *{info['version']}*\n\n"
    # tags
    tag_dict = {}
    for tag in api_json.get('tags', []):
        tag_dict[tag['name']] = {'description': tag['description'], 'paths': ''}
    if not tag_dict.get('default'):
        tag_dict['default'] = {'paths': ''}
    # schemas
    components = api_json.get("components", {})
    schemas = components.get('schemas', {})
    schemas_dict = parse_schemas(schemas)
    # paths
    for route, path in api_json.get('paths', {}).items():
        for method, operation in path.items():
            method_markdown = ''
            summary = operation.get('summary', '*no summary*')
            method_markdown += f"### {summary}\n\n"
            description = operation.get('description', '*no description*')
            method_markdown += f"{description}\n\n"
            method_markdown += f"**route:** `{route}`\n\n"
            method_markdown += f"**method:** `{method.upper()}`\n\n"
            tag = operation.get('tags', ['default'])[0]
            parameters = operation.get('parameters', [])
            if parameters:
                method_markdown += "**parameters:** \n\n"
                method_markdown += parse_parameters(parameters)
            request_body = operation.get('requestBody')
            if request_body:
                method_markdown += "**requestBody:** \n\n"
                method_markdown += parse_request_body(request_body, schemas_dict)
            tag_dict[tag]['paths'] += f"{method_markdown}\n\n"

    for tag, value in tag_dict.items():
        paths = value.get('paths', '')
        if paths:
            markdown += f"## {tag}\n\n"
            markdown += f"{value.get('description', '*no description*')}\n\n"
            markdown += f"{paths}\n"
    if schemas:
        markdown += "## schemas\n\n"
        for name, obj in schemas_dict.items():
            markdown += f"### {name}\n\n"
            markdown += f"{obj}\n\n"

    return markdown
